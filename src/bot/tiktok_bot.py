"""TikTok automation bot using Playwright."""

import random
import time
from typing import Optional, Dict
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout
from tenacity import retry, stop_after_attempt, wait_exponential
from playwright_stealth import Stealth

from src.logger import log
from src.utils import timing
from src.config import config, BROWSER_PROFILES_DIR
from src.bot.stealth import get_stealth_config, apply_stealth_scripts, add_human_behavior, human_scroll


class TikTokBot:
    """Bot for automating TikTok interactions."""

    def __init__(self, agent_id: int, username: str, password: str):
        """Initialize TikTok bot.

        Args:
            agent_id: Database ID of the agent
            username: TikTok username or email
            password: TikTok password
        """
        self.agent_id = agent_id
        self.username = username
        self.password = password
        self.profile_dir = BROWSER_PROFILES_DIR / f"agent_{agent_id}"
        self.profile_dir.mkdir(exist_ok=True)

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _launch_browser(self) -> None:
        """Launch Playwright browser with stealth configuration and optional CAPTCHA solving."""
        log.info(f"[Agent {self.agent_id}] Launching browser...")

        self.playwright = sync_playwright().start()
        stealth_config = get_stealth_config()

        # Browser args for stealth
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials',
            '--lang=en-US',
            '--disable-infobars',
            '--window-size=1920,1080',
        ]

        # Check if we have saved session
        storage_state_path = self.profile_dir / "storage_state.json"
        has_session = storage_state_path.exists()
        log.info(f"[Agent {self.agent_id}] Storage state path: {storage_state_path}, exists: {has_session}")

        # Check if CAPTCHA solver should be used
        # IMPORTANT: ALWAYS use CAPTCHA solver when available, even with saved sessions
        # TikTok can show CAPTCHAs at any time (login, commenting, etc.)
        captcha_solver_available = config.SADCAPTCHA_API_KEY and len(config.SADCAPTCHA_API_KEY) > 0
        use_captcha_solver = captcha_solver_available  # Always use if available
        log.info(f"[Agent {self.agent_id}] CAPTCHA solver available: {captcha_solver_available}, using solver: {use_captcha_solver} (has_session={has_session})")

        if use_captcha_solver:
            try:
                from tiktok_captcha_solver import make_playwright_solver_context
                log.info(f"[Agent {self.agent_id}] Initializing TikTok CAPTCHA solver...")

                # Create context with CAPTCHA solver
                # Note: The solver creates its own context, we'll load session after
                self.context = make_playwright_solver_context(
                    self.playwright,
                    config.SADCAPTCHA_API_KEY,
                    args=browser_args,
                    headless=config.HEADLESS,
                    no_warn=True  # Suppress nodriver recommendation warning
                )
                self.browser = None  # Browser managed by solver
                log.info(f"[Agent {self.agent_id}] CAPTCHA solver initialized")

                # Load saved session if it exists
                if has_session:
                    log.info(f"[Agent {self.agent_id}] Loading saved session for CAPTCHA solver context...")
                    # We need to create a page first, then manually set cookies
                    # This is a workaround since solver context doesn't support storage_state param

            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Failed to init CAPTCHA solver: {e}")
                log.info(f"[Agent {self.agent_id}] Falling back to manual CAPTCHA handling...")
                use_captcha_solver = False

        if not use_captcha_solver:
            # Standard browser launch without CAPTCHA solver
            self.browser = self.playwright.chromium.launch(
                headless=config.HEADLESS,
                args=browser_args,
                channel=None
            )

            # Create context with stealth settings and persistent storage
            self.context = self.browser.new_context(
                viewport=stealth_config["viewport"],
                user_agent=stealth_config["user_agent"],
                locale=stealth_config["locale"],
                timezone_id=stealth_config["timezone_id"],
                color_scheme=stealth_config["color_scheme"],
                storage_state=str(self.profile_dir / "storage_state.json") if (self.profile_dir / "storage_state.json").exists() else None,
                permissions=["geolocation", "notifications"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

        # Create page
        self.page = self.context.new_page()

        # Apply playwright-stealth to hide automation
        log.info(f"[Agent {self.agent_id}] Applying playwright-stealth to hide automation...")
        stealth_config = Stealth()
        stealth_config.apply_stealth_sync(self.page)
        log.info(f"[Agent {self.agent_id}] ✓ Stealth applied - navigator.webdriver and other bot signatures hidden")

        # Load saved cookies if using CAPTCHA solver with existing session
        log.info(f"[Agent {self.agent_id}] Checking if should load session: use_captcha_solver={use_captcha_solver}, has_session={has_session}")
        if use_captcha_solver and has_session:
            try:
                log.info(f"[Agent {self.agent_id}] Loading cookies from {storage_state_path}...")
                import json
                with open(storage_state_path, 'r') as f:
                    state = json.load(f)

                # First navigate to TikTok domain so cookies can be set
                log.info(f"[Agent {self.agent_id}] Navigating to TikTok to set cookies...")
                self.page.goto("https://www.tiktok.com", wait_until="domcontentloaded", timeout=10000)
                self.page.wait_for_timeout(1000)

                # Add cookies to the context (now that we're on the right domain)
                if 'cookies' in state:
                    log.info(f"[Agent {self.agent_id}] Found {len(state['cookies'])} cookies, adding to context...")
                    self.context.add_cookies(state['cookies'])
                    log.info(f"[Agent {self.agent_id}] ✓ Loaded {len(state['cookies'])} cookies into solver context")

                    # Reload the page to apply cookies
                    log.info(f"[Agent {self.agent_id}] Reloading page to apply cookies...")
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_timeout(2000)
                else:
                    log.warning(f"[Agent {self.agent_id}] No cookies found in storage state")

                # Set local storage if available
                if 'origins' in state and len(state['origins']) > 0:
                    for origin_data in state['origins']:
                        if 'localStorage' in origin_data:
                            try:
                                for item in origin_data['localStorage']:
                                    self.page.evaluate(f"localStorage.setItem('{item['name']}', '{item['value']}')")
                                log.info(f"[Agent {self.agent_id}] ✓ Loaded localStorage items")
                            except Exception as e:
                                log.debug(f"[Agent {self.agent_id}] Failed to set localStorage: {e}")
            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Failed to load session into solver context: {e}")

        # Apply stealth scripts
        apply_stealth_scripts(self.page)
        add_human_behavior(self.page)

        # Warmup: Visit a neutral page first to establish browsing patterns
        try:
            self.page.goto("about:blank")
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        log.info(f"[Agent {self.agent_id}] Browser launched successfully")

    def _handle_cookie_consent(self) -> None:
        """Handle TikTok cookie consent banner and GDPR notices."""
        try:
            log.info(f"[Agent {self.agent_id}] Checking for cookie consent and GDPR banners...")
            self.page.wait_for_timeout(1000)

            # First handle cookie consent at bottom
            cookie_consent_selectors = [
                'button:has-text("Allow all")',
                'button:has-text("Accept all")',
                'button:has-text("Accept")',
            ]

            for selector in cookie_consent_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.count() > 0 and button.is_visible(timeout=2000):
                        log.info(f"[Agent {self.agent_id}] Found cookie consent, clicking: {selector}")
                        button.click(timeout=3000)
                        self.page.wait_for_timeout(1000)
                        log.info(f"[Agent {self.agent_id}] ✓ Cookie consent accepted")
                        break
                except Exception:
                    continue

            # Then handle GDPR banner at top (Got it button)
            self.page.wait_for_timeout(1000)
            gdpr_selectors = [
                'button:has-text("Got it")',
                'button:has-text("OK")',
                'button:has-text("Dismiss")',
            ]

            for selector in gdpr_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.count() > 0 and button.is_visible(timeout=2000):
                        log.info(f"[Agent {self.agent_id}] Found GDPR notice, clicking: {selector}")
                        button.click(timeout=3000)
                        self.page.wait_for_timeout(1000)
                        log.info(f"[Agent {self.agent_id}] ✓ GDPR notice dismissed")
                        break
                except Exception:
                    continue

            # Handle keyboard shortcuts popup (close button in top right)
            self.page.wait_for_timeout(1000)
            close_button_selectors = [
                'button[aria-label="Close"]',  # Generic close button
                'button:has-text("×")',         # X button
                'svg[class*="close"] ~ ..',    # SVG close icon's parent button
                'div[role="dialog"] button:first-child',  # First button in dialog
            ]

            for selector in close_button_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.count() > 0 and button.is_visible(timeout=1000):
                        log.info(f"[Agent {self.agent_id}] Found popup close button, clicking: {selector}")
                        button.click(timeout=2000)
                        self.page.wait_for_timeout(500)
                        log.info(f"[Agent {self.agent_id}] ✓ Popup closed")
                        break
                except Exception:
                    continue

            log.info(f"[Agent {self.agent_id}] All banners and popups handled")

        except Exception as e:
            log.debug(f"[Agent {self.agent_id}] Error handling banners: {e}")

    def _save_session(self) -> None:
        """Save browser session state for persistence."""
        if self.context:
            storage_path = self.profile_dir / "storage_state.json"
            self.context.storage_state(path=str(storage_path))
            log.info(f"[Agent {self.agent_id}] Session saved to {storage_path}")

    def _close_browser(self) -> None:
        """Close browser and clean up."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        log.info(f"[Agent {self.agent_id}] Browser closed")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def login(self) -> bool:
        """Login to TikTok account.

        Returns:
            True if login successful, False otherwise
        """
        try:
            log.info(f"[Agent {self.agent_id}] Starting login process...")

            self._launch_browser()

            # First, test basic connectivity with explore page (less strict)
            log.info(f"[Agent {self.agent_id}] Testing TikTok connectivity...")
            urls_to_try = [
                "https://www.tiktok.com/foryou",
                "https://www.tiktok.com/explore",
                "https://www.tiktok.com",
            ]

            connected = False
            for test_url in urls_to_try:
                try:
                    log.info(f"[Agent {self.agent_id}] Trying {test_url}...")
                    self.page.goto(test_url, wait_until="domcontentloaded", timeout=15000)
                    self.page.wait_for_timeout(random.randint(2000, 3000))

                    # If we got here without error, connection works
                    connected = True
                    log.info(f"[Agent {self.agent_id}] ✓ Connected successfully")

                    # Handle cookie consent banner if present
                    self._handle_cookie_consent()

                    # Check if already logged in
                    if self._is_logged_in():
                        log.info(f"[Agent {self.agent_id}] ✓ Already logged in!")
                        self._save_session()
                        return True

                    log.info(f"[Agent {self.agent_id}] Not logged in, need to login")
                    break

                except Exception as e:
                    log.warning(f"[Agent {self.agent_id}] Failed to connect to {test_url}: {str(e)[:100]}")
                    continue

            if not connected:
                log.error(f"[Agent {self.agent_id}] ✗ Could not connect to TikTok (all URLs failed)")
                log.error(f"[Agent {self.agent_id}] This might be a network issue or TikTok blocking")
                return False

            # Navigate to login page
            log.info(f"[Agent {self.agent_id}] Navigating to login page...")
            try:
                self.page.goto("https://www.tiktok.com/login/phone-or-email/email", wait_until="domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(random.randint(3000, 5000))  # Wait longer for redirects
            except Exception as e:
                log.error(f"[Agent {self.agent_id}] Failed to reach login page: {e}")
                # Try alternative login URL
                log.info(f"[Agent {self.agent_id}] Trying alternative login URL...")
                self.page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded", timeout=15000)
                self.page.wait_for_timeout(random.randint(3000, 5000))

            # Check current URL - might have been redirected if already logged in
            current_url = self.page.url
            log.info(f"[Agent {self.agent_id}] Current URL after navigation: {current_url}")

            # If not on login page anymore, check if logged in
            if "/login" not in current_url:
                log.info(f"[Agent {self.agent_id}] Redirected away from login page, checking login status...")
                if self._is_logged_in():
                    log.info(f"[Agent {self.agent_id}] ✓ Already logged in (redirected)!")
                    self._save_session()
                    return True

            # Double-check if login page shows we're already logged in
            if self._is_logged_in():
                log.info(f"[Agent {self.agent_id}] ✓ Already logged in!")
                self._save_session()
                return True

            # Fill in username/email
            log.info(f"[Agent {self.agent_id}] Entering credentials...")
            email_input = self.page.locator('input[type="text"][name="username"]').first
            if email_input.count() == 0:
                # Try alternative selector
                email_input = self.page.locator('input[placeholder*="Email"]').first

            self._human_type(email_input, self.username)
            self.page.wait_for_timeout(random.randint(1000, 2000))

            # Fill in password
            password_input = self.page.locator('input[type="password"]').first
            self._human_type(password_input, self.password)
            self.page.wait_for_timeout(random.randint(1000, 2000))

            # Click login button
            log.info(f"[Agent {self.agent_id}] Clicking login button...")
            login_button = self.page.locator('button[type="submit"]').first
            if login_button.count() == 0:
                login_button = self.page.locator('button:has-text("Log in")').first

            login_button.click()

            # Wait for login to complete
            log.info(f"[Agent {self.agent_id}] Waiting for login to complete...")
            self.page.wait_for_timeout(random.randint(3000, 5000))

            # Check if CAPTCHA appeared - wait for SadCaptcha solver to handle it
            if self._has_captcha():
                log.warning(f"[Agent {self.agent_id}] ⚠ CAPTCHA detected during login!")
                log.info(f"[Agent {self.agent_id}] Waiting for SadCaptcha solver to handle it...")
                # Wait up to 60 seconds for CAPTCHA to be solved automatically
                for i in range(12):  # 12 x 5 seconds = 60 seconds
                    self.page.wait_for_timeout(5000)
                    if not self._has_captcha():
                        log.info(f"[Agent {self.agent_id}] ✓ CAPTCHA appears to be solved!")
                        break
                    log.info(f"[Agent {self.agent_id}] Still waiting for CAPTCHA solver... ({(i+1)*5}s)")
                else:
                    log.error(f"[Agent {self.agent_id}] ✗ CAPTCHA not solved after 60 seconds")
                    return False

            # Wait a moment for page to settle after potential CAPTCHA
            self.page.wait_for_timeout(2000)

            # Verify login success
            if self._is_logged_in():
                log.info(f"[Agent {self.agent_id}] ✓ Login successful!")
                self._save_session()
                return True
            else:
                log.error(f"[Agent {self.agent_id}] ✗ Login failed")
                return False

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Login error: {e}")
            return False

    def _is_logged_in(self) -> bool:
        """Check if currently logged in to TikTok.

        Returns:
            True if logged in
        """
        try:
            # Wait a moment for page to stabilize
            self.page.wait_for_timeout(2000)

            log.info(f"[Agent {self.agent_id}] Checking login status on URL: {self.page.url}")

            # FIRST: Check for "Log in" button - if it exists, we're definitely NOT logged in
            log.info(f"[Agent {self.agent_id}] Starting login button check...")
            try:
                # Try multiple selectors to find the login button
                login_button_selectors = [
                    'button:has-text("Log in"):visible',  # Any visible "Log in" button
                    'a:has-text("Log in"):visible',       # Login link
                    '[data-e2e="login-button"]:visible',  # Data attribute
                ]

                for selector in login_button_selectors:
                    try:
                        btn = self.page.locator(selector).first
                        count = btn.count()
                        if count > 0:
                            log.info(f"[Agent {self.agent_id}] ✗ Not logged in - found login button with selector: {selector}")
                            return False
                    except Exception as e:
                        # Selector not found, try next
                        continue

                log.info(f"[Agent {self.agent_id}] No login button found, checking logged-in indicators...")

            except Exception as e:
                log.info(f"[Agent {self.agent_id}] Login button check failed: {e}")

            # SECOND: Check for logged-in indicators (but only if no "Log in" button found)
            logged_in_indicators = [
                '[data-e2e="profile-icon"]',  # Profile avatar icon (most reliable)
                '[data-e2e="nav-profile"]',    # Profile nav item
                'div[data-e2e="user-avatar"]', # User avatar
            ]

            for selector in logged_in_indicators:
                try:
                    elem = self.page.locator(selector).first
                    count = elem.count()
                    log.info(f"[Agent {self.agent_id}] Checking logged-in indicator: {selector}, count: {count}")
                    if count > 0:
                        try:
                            is_visible = elem.is_visible(timeout=3000)
                            log.info(f"[Agent {self.agent_id}] Element visible: {is_visible}")
                            if is_visible:
                                log.info(f"[Agent {self.agent_id}] ✓ Login confirmed via: {selector}")
                                return True
                        except Exception as ve:
                            log.info(f"[Agent {self.agent_id}] Visibility check failed: {ve}")
                            continue
                except Exception as e:
                    log.info(f"[Agent {self.agent_id}] Selector check failed: {e}")
                    continue

            # If no indicators found, take screenshot for debugging
            log.warning(f"[Agent {self.agent_id}] No clear login indicators found, taking screenshot for debug...")
            try:
                screenshot_path = f"data/debug_login_check_{self.agent_id}.png"
                self.page.screenshot(path=screenshot_path)
                log.info(f"[Agent {self.agent_id}] Screenshot saved: {screenshot_path}")
            except:
                pass

            log.warning(f"[Agent {self.agent_id}] Assuming not logged in")
            return False

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Error checking login status: {e}")
            return False

    def _close_popups_and_modals(self, skip_captcha: bool = True) -> None:
        """Close any popups, modals, or overlays that might be blocking interaction.

        Args:
            skip_captcha: If True, don't close CAPTCHA popups (let solver handle them)
        """
        try:
            # Wait a moment for any popups to appear
            self.page.wait_for_timeout(500)

            # If CAPTCHA solving is enabled and we should skip CAPTCHAs, check first
            if skip_captcha and self._has_captcha():
                log.info(f"[Agent {self.agent_id}] CAPTCHA detected, skipping popup closure to let solver handle it...")
                return

            # Check specifically for keyboard shortcuts popup
            keyboard_shortcuts_selectors = [
                'text="Introducing keyboard shortcuts!"',
                'h2:has-text("keyboard shortcuts")',
                'div:has-text("Introducing keyboard shortcuts")',
            ]

            for ks_selector in keyboard_shortcuts_selectors:
                try:
                    if self.page.locator(ks_selector).count() > 0:
                        log.info(f"[Agent {self.agent_id}] Detected keyboard shortcuts popup, closing...")
                        # Try to find and click the close button (X in top right)
                        close_selectors = [
                            'button[aria-label="Close"]',
                            'button:near(:text("keyboard shortcuts"))',
                            'svg[data-e2e="close"]:near(:text("keyboard shortcuts"))',
                        ]

                        for close_sel in close_selectors:
                            try:
                                close_btn = self.page.locator(close_sel).first
                                if close_btn.count() > 0 and close_btn.is_visible(timeout=1000):
                                    close_btn.click(timeout=2000)
                                    self.page.wait_for_timeout(1000)
                                    log.info(f"[Agent {self.agent_id}] ✓ Closed keyboard shortcuts popup")
                                    return
                            except Exception:
                                continue

                        # If clicking didn't work, try Escape key
                        log.info(f"[Agent {self.agent_id}] Trying Escape key to close popup...")
                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue

            # List of other non-CAPTCHA popup selectors
            popup_close_selectors = [
                'button:has-text("Got it")',
                'button:has-text("Dismiss")',
                'button:has-text("OK")',
            ]

            for selector in popup_close_selectors:
                try:
                    elems = self.page.locator(selector)
                    if elems.count() > 0:
                        for i in range(min(2, elems.count())):
                            try:
                                elem = elems.nth(i)
                                if elem.is_visible(timeout=1000):
                                    log.info(f"[Agent {self.agent_id}] Found popup: {selector}, closing...")
                                    elem.click(timeout=2000)
                                    self.page.wait_for_timeout(1000)
                                    log.info(f"[Agent {self.agent_id}] ✓ Closed popup")
                                    return
                            except Exception:
                                continue
                except Exception:
                    continue

        except Exception as e:
            log.debug(f"[Agent {self.agent_id}] Error in _close_popups_and_modals: {e}")

    def _has_captcha(self) -> bool:
        """Check if CAPTCHA is present.

        Returns:
            True if CAPTCHA detected
        """
        try:
            # Check for common CAPTCHA indicators
            captcha_indicators = [
                'iframe[title*="captcha"]',
                '[class*="captcha"]',
                '#captcha',
                'div:has-text("Verify")',
                'div:has-text("puzzle")',  # TikTok puzzle CAPTCHA
                'div:has-text("Drag the slider")',  # TikTok slider CAPTCHA
                '[class*="verify"]',
                '[data-e2e="captcha"]',
            ]

            for selector in captcha_indicators:
                if self.page.locator(selector).count() > 0:
                    log.debug(f"[Agent {self.agent_id}] CAPTCHA detected with selector: {selector}")
                    return True

            return False
        except Exception as e:
            log.debug(f"[Agent {self.agent_id}] Error checking for CAPTCHA: {e}")
            return False

    def _human_type(self, element, text: str, wpm: int = None) -> None:
        """Type text with human-like delays.

        Args:
            element: Playwright locator/element
            text: Text to type
            wpm: Words per minute (uses config default if None)
        """
        if wpm is None:
            wpm = config.TYPING_SPEED_WPM

        element.click()
        self.page.wait_for_timeout(random.randint(200, 500))

        # Type character by character
        for char in text:
            element.type(char, delay=random.randint(50, 150))
            # Occasionally pause (like a human would)
            if random.random() < 0.1:
                self.page.wait_for_timeout(random.randint(200, 600))

    def navigate_to_explore(self) -> bool:
        """Navigate to Explore page to find trending/popular videos.

        Returns:
            True if navigation successful
        """
        try:
            log.info(f"[Agent {self.agent_id}] Navigating to Explore page (trending content)...")

            # If browser not open, launch it
            if not self.page:
                self._launch_browser()

            # Navigate to explore page
            self.page.goto("https://www.tiktok.com/explore", wait_until="domcontentloaded")
            self.page.wait_for_timeout(random.randint(3000, 5000))

            # Try to click on "Trending" or "Popular" tab if it exists
            # This ensures we're not on the "Following" tab
            log.info(f"[Agent {self.agent_id}] Looking for Trending/Popular tab...")
            trending_selectors = [
                'a[href*="trending"]',
                'div[data-e2e="explore-trending"]',
                'button:has-text("Trending")',
                'a:has-text("Trending")',
                # Sometimes it's organized differently
                '[role="tab"]:has-text("Trending")',
            ]

            clicked_trending = False
            for selector in trending_selectors:
                try:
                    elem = self.page.locator(selector).first
                    if elem.count() > 0 and elem.is_visible(timeout=2000):
                        log.info(f"[Agent {self.agent_id}] Found Trending tab, clicking...")
                        elem.click(timeout=3000)
                        self.page.wait_for_timeout(random.randint(2000, 3000))
                        clicked_trending = True
                        break
                except Exception:
                    continue

            if not clicked_trending:
                log.info(f"[Agent {self.agent_id}] No Trending tab found, using default Explore view")

            # Random scrolling to appear human and load more videos
            scroll_times = random.randint(2, 4)
            for _ in range(scroll_times):
                human_scroll(self.page, "down")
                self.page.wait_for_timeout(random.randint(2000, 3000))

            log.info(f"[Agent {self.agent_id}] ✓ Successfully navigated to Explore (trending content)")
            return True

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Navigation error: {e}")
            return False

    def navigate_to_for_you(self) -> bool:
        """Navigate to For You page.

        Returns:
            True if navigation successful
        """
        try:
            log.info(f"[Agent {self.agent_id}] Navigating to For You page...")

            # If browser not open, launch it
            if not self.page:
                self._launch_browser()

            self.page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded")
            self.page.wait_for_timeout(random.randint(3000, 5000))

            # Random scrolling to appear human
            scroll_times = random.randint(2, 5)
            for _ in range(scroll_times):
                human_scroll(self.page, "down")
                self.page.wait_for_timeout(random.randint(2000, 4000))

            log.info(f"[Agent {self.agent_id}] ✓ Successfully navigated to For You")
            return True

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Navigation error: {e}")
            return False

    def click_into_video(self) -> bool:
        """Click on a video in the feed to open the full video view with comments.

        Returns:
            True if successfully clicked into a video
        """
        try:
            log.info(f"[Agent {self.agent_id}] Looking for video to open...")

            # Wait for videos to load
            self.page.wait_for_timeout(2000)

            # Strategy 1: Direct navigation (most reliable) - extract URL and navigate
            log.info(f"[Agent {self.agent_id}] Looking for video URLs in page...")
            video_links = self.page.locator('a[href*="/video/"]').all()

            if video_links and len(video_links) > 0:
                # Pick a random video from available links
                num_videos = len(video_links)
                log.info(f"[Agent {self.agent_id}] Found {num_videos} video links")

                # Pick a random one from a wider range for more variety
                # Skip first 2-3 videos to avoid repetition, pick from next 20-30
                start_index = min(2, num_videos - 1)
                end_index = min(num_videos, 30)  # Pick from first 30 videos
                random_indices = list(range(start_index, end_index))
                random.shuffle(random_indices)

                # Try to get href from random links
                for i in random_indices[:5]:  # Try 5 random videos
                    try:
                        link = video_links[i]
                        video_url = link.get_attribute('href')
                        if video_url:
                            # Make sure it's a full URL
                            if not video_url.startswith('http'):
                                video_url = f"https://www.tiktok.com{video_url}"

                            log.info(f"[Agent {self.agent_id}] Navigating to video #{i+1}: {video_url}")
                            self.page.goto(video_url, wait_until="domcontentloaded")
                            self.page.wait_for_timeout(random.randint(3000, 5000))

                            if "/video/" in self.page.url:
                                log.info(f"[Agent {self.agent_id}] ✓ Successfully opened video: {self.page.url}")
                                return True
                    except Exception as e:
                        log.debug(f"[Agent {self.agent_id}] Failed to navigate to video #{i+1}: {e}")
                        continue

            # Strategy 2: Try clicking on visible video element
            log.info(f"[Agent {self.agent_id}] Trying to click visible video elements...")
            video_selectors = [
                'video',
                '[data-e2e="recommend-list-item-container"] video',
            ]

            for selector in video_selectors:
                elems = self.page.locator(selector)
                if elems.count() > 0:
                    log.info(f"[Agent {self.agent_id}] Found {elems.count()} video(s) with selector: {selector}")

                    # Try clicking each video element (up to 3)
                    for i in range(min(3, elems.count())):
                        try:
                            elem = elems.nth(i)
                            # Check if visible
                            if elem.is_visible():
                                elem.click(timeout=3000)
                                self.page.wait_for_timeout(random.randint(3000, 5000))

                                if "/video/" in self.page.url:
                                    log.info(f"[Agent {self.agent_id}] ✓ Opened video via click: {self.page.url}")
                                    return True
                            else:
                                log.debug(f"[Agent {self.agent_id}] Video element {i} not visible, skipping")
                        except Exception as e:
                            log.debug(f"[Agent {self.agent_id}] Click failed on video {i}: {e}")
                            continue

            log.error(f"[Agent {self.agent_id}] Could not open any video. Current URL: {self.page.url}")
            return False

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Error opening video: {e}")
            return False

    def get_video_info(self) -> Optional[Dict[str, str]]:
        """Extract current video information.

        Returns:
            Dict with video_url, description, creator, etc. or None
        """
        try:
            log.info(f"[Agent {self.agent_id}] Extracting video information...")

            # Get current URL
            video_url = self.page.url

            # Extract video description
            description_selectors = [
                '[data-e2e="browse-video-desc"]',
                '[data-e2e="video-desc"]',
                'h1[data-e2e="browse-video-desc"]',
                '.video-meta-caption',
            ]

            description = ""
            for selector in description_selectors:
                desc_elem = self.page.locator(selector).first
                if desc_elem.count() > 0:
                    description = desc_elem.text_content().strip()
                    break

            # Extract creator username
            creator_selectors = [
                '[data-e2e="browse-username"]',
                '[data-e2e="video-author-uniqueid"]',
                '.author-uniqueId',
            ]

            creator = ""
            for selector in creator_selectors:
                creator_elem = self.page.locator(selector).first
                if creator_elem.count() > 0:
                    creator = creator_elem.text_content().strip()
                    break

            video_info = {
                "video_url": video_url,
                "description": description or "No description",
                "creator": creator or "Unknown",
            }

            log.info(f"[Agent {self.agent_id}] ✓ Video info extracted: {creator} - {description[:50]}...")
            return video_info

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Video extraction error: {e}")
            return None

    def post_comment(self, comment_text: str) -> bool:
        """Post a comment on current video.

        Args:
            comment_text: The comment to post

        Returns:
            True if comment posted successfully
        """
        try:
            log.info(f"[Agent {self.agent_id}] Posting comment: {comment_text[:50]}...")

            # Wait for page to fully load
            self.page.wait_for_timeout(3000)

            # Check for CAPTCHA - wait for SadCaptcha solver to handle it
            if self._has_captcha():
                log.warning(f"[Agent {self.agent_id}] ⚠ CAPTCHA detected before commenting!")

                # Save screenshot
                try:
                    screenshot_path = f"data/captcha_detected_{self.agent_id}.png"
                    self.page.screenshot(path=screenshot_path)
                    log.info(f"[Agent {self.agent_id}] CAPTCHA screenshot saved: {screenshot_path}")
                except:
                    pass

                # Wait for SadCaptcha solver to handle it automatically (up to 60 seconds)
                log.info(f"[Agent {self.agent_id}] Waiting for SadCaptcha solver to handle it...")
                for i in range(12):  # 12 x 5 seconds = 60 seconds
                    self.page.wait_for_timeout(5000)
                    if not self._has_captcha():
                        log.info(f"[Agent {self.agent_id}] ✓ CAPTCHA appears to be solved!")
                        break
                    log.info(f"[Agent {self.agent_id}] Still waiting for CAPTCHA solver... ({(i+1)*5}s)")
                else:
                    log.error(f"[Agent {self.agent_id}] ✗ CAPTCHA not solved after 60 seconds")
                    return False

                # Check if CAPTCHA is still there
                if self._has_captcha():
                    log.error(f"[Agent {self.agent_id}] ✗ CAPTCHA still present after 60 seconds")
                    return False
                else:
                    log.info(f"[Agent {self.agent_id}] ✓ CAPTCHA appears to be solved, continuing...")

            # First, click the comment button/icon to open comment section
            log.info(f"[Agent {self.agent_id}] Looking for comment button to open comment section...")
            comment_button_selectors = [
                '[data-e2e="browse-comment"]',  # Comment button
                '[data-e2e="comment-icon"]',
                'button[aria-label*="comment"]',
                'button[aria-label*="Comment"]',
                '[class*="comment"][class*="button"]',
                'svg[class*="comment"]',  # SVG icon for comments
            ]

            comment_opened = False
            for selector in comment_button_selectors:
                elems = self.page.locator(selector)
                if elems.count() > 0:
                    log.info(f"[Agent {self.agent_id}] Found comment button with: {selector}")
                    try:
                        # Click the first visible one
                        for i in range(min(3, elems.count())):
                            elem = elems.nth(i)
                            if elem.is_visible():
                                elem.click(timeout=3000)
                                self.page.wait_for_timeout(2000)
                                log.info(f"[Agent {self.agent_id}] Clicked comment button, waiting for comment section to open...")
                                comment_opened = True
                                break
                        if comment_opened:
                            break
                    except Exception as e:
                        log.debug(f"[Agent {self.agent_id}] Failed to click comment button with {selector}: {e}")
                        continue

            if not comment_opened:
                log.warning(f"[Agent {self.agent_id}] Could not find/click comment button, trying to scroll to comments...")
                # Scroll down as fallback
                self.page.evaluate("window.scrollBy(0, 300)")
                self.page.wait_for_timeout(2000)

            # Check for CAPTCHA first - if detected, wait for solver
            if self._has_captcha():
                log.warning(f"[Agent {self.agent_id}] ⚠ CAPTCHA detected after clicking comment button!")
                log.info(f"[Agent {self.agent_id}] Waiting for SadCaptcha solver to handle it...")
                # Wait up to 60 seconds for CAPTCHA to be solved automatically
                for i in range(12):  # 12 x 5 seconds = 60 seconds
                    self.page.wait_for_timeout(5000)
                    if not self._has_captcha():
                        log.info(f"[Agent {self.agent_id}] ✓ CAPTCHA appears to be solved!")
                        break
                    log.info(f"[Agent {self.agent_id}] Still waiting for CAPTCHA solver... ({(i+1)*5}s)")

                # Check if still there after 60 seconds
                if self._has_captcha():
                    log.error(f"[Agent {self.agent_id}] ✗ CAPTCHA still present after 60 seconds")
                    return False

            # Close non-CAPTCHA popups (like keyboard shortcuts)
            self._close_popups_and_modals(skip_captcha=True)
            self.page.wait_for_timeout(1000)

            # Find comment input box
            comment_selectors = [
                '[data-e2e="comment-input"]',
                '[placeholder*="Add comment"]',
                '[placeholder*="add a comment"]',
                '[placeholder*="comment"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="comment"]',
                'input[placeholder*="comment"]',
            ]

            comment_input = None
            for selector in comment_selectors:
                elem = self.page.locator(selector).first
                if elem.count() > 0:
                    log.info(f"[Agent {self.agent_id}] Found comment input with: {selector}")
                    comment_input = elem
                    break

            # If still no comment input, the comments panel might not be open
            # Try clicking the "Comments" tab explicitly
            if not comment_input:
                log.info(f"[Agent {self.agent_id}] Comment input not found, trying to click Comments tab...")
                comments_tab_selectors = [
                    'button:has-text("Comments")',
                    'div:has-text("Comments")',
                    '[role="tab"]:has-text("Comments")',
                    'span:has-text("Comments")',
                ]

                for selector in comments_tab_selectors:
                    try:
                        elem = self.page.locator(selector).first
                        if elem.count() > 0 and elem.is_visible(timeout=2000):
                            log.info(f"[Agent {self.agent_id}] Found Comments tab with: {selector}, clicking...")
                            elem.click(timeout=3000)
                            self.page.wait_for_timeout(2000)

                            # Try to find comment input again
                            for input_selector in comment_selectors:
                                elem2 = self.page.locator(input_selector).first
                                if elem2.count() > 0:
                                    log.info(f"[Agent {self.agent_id}] ✓ Found comment input after clicking tab: {input_selector}")
                                    comment_input = elem2
                                    break
                            if comment_input:
                                break
                    except Exception as e:
                        log.debug(f"[Agent {self.agent_id}] Failed to click Comments tab with {selector}: {e}")
                        continue

            if not comment_input:
                log.error(f"[Agent {self.agent_id}] ✗ Could not find comment input box")
                # Take screenshot for debugging
                try:
                    screenshot_path = f"data/debug_no_comment_box_{self.agent_id}.png"
                    self.page.screenshot(path=screenshot_path)
                    log.info(f"[Agent {self.agent_id}] Screenshot saved: {screenshot_path}")
                except:
                    pass
                return False

            # Close any popups that might appear - be VERY aggressive
            self._close_popups_and_modals()

            # Directly remove the keyboard shortcuts popup container if it exists
            log.info(f"[Agent {self.agent_id}] Removing keyboard shortcuts popup overlay...")
            try:
                # Use JavaScript to remove the popup container directly
                self.page.evaluate("""
                    const popup = document.querySelector('.css-1oz3gmx-7937d88b--DivKeyboardShortcutContainer, .DivKeyboardShortcutContainer, [class*="KeyboardShortcut"]');
                    if (popup) {
                        popup.remove();
                        console.log('Removed keyboard shortcuts popup');
                    }
                """)
                self.page.wait_for_timeout(500)
            except Exception as e:
                log.debug(f"[Agent {self.agent_id}] Popup removal script error: {e}")

            # Also press Escape as backup
            for _ in range(2):
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(200)

            # Click comment input with force if needed
            log.info(f"[Agent {self.agent_id}] Clicking comment input box...")
            try:
                comment_input.click(timeout=5000)
            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Regular click failed, trying force click: {e}")
                try:
                    comment_input.click(force=True)
                except Exception as e2:
                    log.error(f"[Agent {self.agent_id}] Force click also failed: {e2}")
                    # Take screenshot
                    try:
                        screenshot_path = f"data/debug_click_failed_{self.agent_id}.png"
                        self.page.screenshot(path=screenshot_path)
                        log.info(f"[Agent {self.agent_id}] Screenshot saved: {screenshot_path}")
                    except:
                        pass
                    return False

            self.page.wait_for_timeout(random.randint(1000, 2000))

            # Type comment using human-like keyboard input (REQUIRED for React state)
            log.info(f"[Agent {self.agent_id}] Typing comment: {comment_text[:30]}...")
            # TikTok's React requires REAL keyboard events - JavaScript doesn't enable Post button
            self._human_type(comment_input, comment_text)
            self.page.wait_for_timeout(random.randint(1500, 2500))

            # Verify comment was typed
            try:
                typed_value = comment_input.input_value() if hasattr(comment_input, 'input_value') else None
                if typed_value:
                    log.info(f"[Agent {self.agent_id}] ✓ Comment typed successfully (length: {len(typed_value)})")
                else:
                    # For contenteditable divs, check text_content
                    typed_value = comment_input.text_content()
                    log.info(f"[Agent {self.agent_id}] ✓ Comment typed successfully (contenteditable, length: {len(typed_value) if typed_value else 0})")

                if not typed_value or len(typed_value) < 5:
                    log.error(f"[Agent {self.agent_id}] ✗ Comment not typed properly (too short or empty)")
                    return False
            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Could not verify typed comment: {e}")

            # Find and click post button
            log.info(f"[Agent {self.agent_id}] Looking for post button...")
            post_button_selectors = [
                '[data-e2e="comment-post"]',
                'button:has-text("Post")',
                'div[role="button"]:has-text("Post")',
                'button:has-text("post")',  # Lowercase
                '[aria-label*="post"]',
                '[aria-label*="Post"]',
            ]

            post_button = None
            for selector in post_button_selectors:
                elem = self.page.locator(selector).first
                if elem.count() > 0:
                    log.info(f"[Agent {self.agent_id}] Found post button with: {selector}")
                    post_button = elem
                    break

            if not post_button:
                log.error(f"[Agent {self.agent_id}] ✗ Could not find post button")
                # Take screenshot
                try:
                    screenshot_path = f"data/debug_no_post_button_{self.agent_id}.png"
                    self.page.screenshot(path=screenshot_path)
                    log.info(f"[Agent {self.agent_id}] Screenshot saved: {screenshot_path}")
                except:
                    pass
                return False

            # Wait for Post button to become enabled (sometimes takes a moment after typing)
            log.info(f"[Agent {self.agent_id}] Waiting for post button to be enabled...")
            self.page.wait_for_timeout(1500)

            # Check if button is enabled
            try:
                is_enabled = post_button.is_enabled()
                is_visible = post_button.is_visible()
                log.info(f"[Agent {self.agent_id}] Post button state: enabled={is_enabled}, visible={is_visible}")

                if not is_enabled:
                    log.warning(f"[Agent {self.agent_id}] Post button is disabled, waiting 2 more seconds...")
                    self.page.wait_for_timeout(2000)
            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Could not check button state: {e}")

            # Take screenshot before clicking
            try:
                screenshot_path = f"data/debug_before_post_{self.agent_id}.png"
                self.page.screenshot(path=screenshot_path)
                log.info(f"[Agent {self.agent_id}] Pre-click screenshot: {screenshot_path}")
            except:
                pass

            # Try multiple submission strategies
            log.info(f"[Agent {self.agent_id}] Attempting to submit comment...")
            submitted = False

            # Strategy 1: Try Cmd+Enter (Mac) / Ctrl+Enter keyboard shortcut first
            try:
                log.info(f"[Agent {self.agent_id}] Trying Cmd+Enter keyboard shortcut...")
                comment_input.focus()
                self.page.wait_for_timeout(300)
                # Try both Cmd (Mac) and Ctrl (Windows/Linux)
                self.page.keyboard.press("Meta+Enter")  # Mac
                self.page.wait_for_timeout(500)
                log.info(f"[Agent {self.agent_id}] ✓ Pressed Cmd+Enter")
                submitted = True
            except Exception as e:
                log.debug(f"[Agent {self.agent_id}] Cmd+Enter failed: {e}")
                try:
                    self.page.keyboard.press("Control+Enter")  # Windows/Linux
                    log.info(f"[Agent {self.agent_id}] ✓ Pressed Ctrl+Enter")
                    submitted = True
                except Exception as e2:
                    log.debug(f"[Agent {self.agent_id}] Ctrl+Enter also failed: {e2}")

            # Strategy 2: Click post button
            if not submitted:
                log.info(f"[Agent {self.agent_id}] Keyboard shortcut didn't work, clicking post button...")
                clicked = False

                # Try regular click with hover
                try:
                    post_button.hover()
                    self.page.wait_for_timeout(500)
                    post_button.click(timeout=5000)
                    log.info(f"[Agent {self.agent_id}] ✓ Post button clicked (regular with hover)")
                    clicked = True
                    submitted = True
                except Exception as e:
                    log.warning(f"[Agent {self.agent_id}] Regular click failed: {e}")

                    # Try force click
                    try:
                        post_button.click(force=True, timeout=3000)
                        log.info(f"[Agent {self.agent_id}] ✓ Post button clicked (force)")
                        clicked = True
                        submitted = True
                    except Exception as e2:
                        log.warning(f"[Agent {self.agent_id}] Force click failed: {e2}")

                        # Try JavaScript click via element handle
                        try:
                            handle = post_button.element_handle()
                            if handle:
                                self.page.evaluate("(el) => el.click()", handle)
                                log.info(f"[Agent {self.agent_id}] ✓ Post button clicked (JavaScript)")
                                clicked = True
                                submitted = True
                            else:
                                log.error(f"[Agent {self.agent_id}] Could not get element handle")
                        except Exception as e3:
                            log.error(f"[Agent {self.agent_id}] JavaScript click failed: {e3}")

            if not submitted:
                log.error(f"[Agent {self.agent_id}] ✗ All submission strategies failed")
                try:
                    screenshot_path = f"data/debug_submit_failed_{self.agent_id}.png"
                    self.page.screenshot(path=screenshot_path)
                    log.info(f"[Agent {self.agent_id}] Failed submission screenshot: {screenshot_path}")
                except:
                    pass
                return False

            # Wait for posting and check for errors
            self.page.wait_for_timeout(2000)

            # Check for error messages that might appear
            error_indicators = [
                'text="Try again later"',
                'text="Something went wrong"',
                'text="slow down"',
                'text="Please wait"',
                '[class*="error"]',
                '[class*="Error"]',
            ]

            for error_selector in error_indicators:
                if self.page.locator(error_selector).count() > 0:
                    error_elem = self.page.locator(error_selector).first
                    if error_elem.is_visible():
                        error_text = error_elem.text_content()
                        log.error(f"[Agent {self.agent_id}] ✗ TikTok error after posting: {error_text}")
                        return False

            # Wait for comment to appear in comments list
            log.info(f"[Agent {self.agent_id}] Waiting for comment to appear in comments list...")
            self.page.wait_for_timeout(3000)

            # Verify comment posted - CHECK ACTUAL COMMENTS LIST
            comment_appeared = False

            # Method 1: Check if our comment appears in the comments list (MOST RELIABLE)
            try:
                log.info(f"[Agent {self.agent_id}] Checking comments list for our comment...")
                comment_texts = self.page.evaluate("""
                    () => {
                        const comments = Array.from(document.querySelectorAll('[data-e2e="comment-level-1"]'));
                        return comments.slice(0, 15).map(c => {
                            const textEl = c.querySelector('[data-e2e="comment-text"]') ||
                                          c.querySelector('[class*="CommentText"]') ||
                                          c.querySelector('p') ||
                                          c.querySelector('span');
                            return textEl ? textEl.textContent.trim() : '';
                        }).filter(t => t.length > 0);
                    }
                """)

                log.info(f"[Agent {self.agent_id}] Found {len(comment_texts)} comments in list")

                # Check if our comment appears in the list (check first 30 chars for match)
                comment_start = comment_text[:30].strip()
                for i, comment in enumerate(comment_texts):
                    if comment_start in comment or comment in comment_text:
                        comment_appeared = True
                        log.info(f"[Agent {self.agent_id}] ✓ Found our comment in comments list at position {i+1}!")
                        log.info(f"[Agent {self.agent_id}] Comment preview: {comment[:60]}...")
                        break

                if not comment_appeared and len(comment_texts) > 0:
                    log.warning(f"[Agent {self.agent_id}] Our comment NOT found in list")
                    log.warning(f"[Agent {self.agent_id}] Recent comments: {[c[:40] for c in comment_texts[:3]]}")

            except Exception as e:
                log.warning(f"[Agent {self.agent_id}] Error checking comments list: {e}")

            # Method 2: Look for comment input being cleared (FALLBACK - not reliable)
            input_cleared = False
            try:
                # Try input_value for regular inputs
                comment_input_value = comment_input.input_value()
                input_cleared = comment_input_value == ""
            except Exception:
                # Try text_content for contenteditable divs
                try:
                    comment_input_text = comment_input.text_content()
                    # Check if truly empty OR if it shows the placeholder text
                    placeholders = ["Add comment...", "Añadir comentario", "Add a comment"]
                    is_empty = not comment_input_text or len(comment_input_text.strip()) == 0
                    is_placeholder = any(ph in comment_input_text for ph in placeholders)
                    input_cleared = is_empty or is_placeholder
                    log.debug(f"[Agent {self.agent_id}] Contenteditable check: text='{comment_input_text}', is_empty={is_empty}, is_placeholder={is_placeholder}")
                except Exception as e:
                    log.debug(f"[Agent {self.agent_id}] Could not check contenteditable text: {e}")
                    pass

            # Method 3: Check if post button is disabled/gone (sometimes happens after posting)
            post_button_gone = False
            try:
                post_button_gone = post_button.count() == 0 or not post_button.is_enabled()
            except Exception:
                pass

            log.info(f"[Agent {self.agent_id}] Verification: comment_appeared={comment_appeared}, input_cleared={input_cleared}, post_button_gone={post_button_gone}")

            # ONLY return True if comment actually appears in the list
            if comment_appeared:
                log.info(f"[Agent {self.agent_id}] ✓ Comment posted successfully! (verified in comments list)")
                return True
            else:
                # Take a screenshot to see what's happening
                try:
                    screenshot_path = f"data/debug_after_post_{self.agent_id}.png"
                    self.page.screenshot(path=screenshot_path)
                    log.info(f"[Agent {self.agent_id}] Screenshot saved: {screenshot_path}")
                except:
                    pass

                log.error(f"[Agent {self.agent_id}] ✗ Comment NOT found in comments list - posting failed!")
                log.error(f"[Agent {self.agent_id}] Input cleared: {input_cleared}, but comment not in list")
                log.error(f"[Agent {self.agent_id}] Check screenshots: debug_before_post_{self.agent_id}.png and debug_after_post_{self.agent_id}.png")
                return False  # Only return True if comment actually appears in list

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Comment posting error: {e}")
            return False

    def run_comment_cycle(self, comment_text: str) -> Dict[str, any]:
        """Execute a full comment cycle: navigate, extract, comment.

        Args:
            comment_text: The comment to post

        Returns:
            Dict with status, video_info, error (if any)
        """
        result = {
            "status": "failed",
            "video_info": None,
            "error": None
        }

        try:
            # Navigate to For You page
            if not self.navigate_to_for_you():
                result["error"] = "Failed to navigate to For You page"
                return result

            # Extract video info
            video_info = self.get_video_info()
            if not video_info:
                result["error"] = "Failed to extract video information"
                return result

            result["video_info"] = video_info

            # Post comment
            if self.post_comment(comment_text):
                result["status"] = "posted"
                log.info(f"[Agent {self.agent_id}] ✓ Comment cycle completed successfully!")
            else:
                result["status"] = "failed"
                result["error"] = "Failed to post comment"

        except Exception as e:
            log.error(f"[Agent {self.agent_id}] Comment cycle error: {e}")
            result["error"] = str(e)

        finally:
            # Save session and close browser
            self._save_session()
            self._close_browser()

        return result
