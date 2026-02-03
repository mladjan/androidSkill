"""Script to import a fresh TikTok session for agent 1 by logging in manually."""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from src.config import BROWSER_PROFILES_DIR
from src.logger import log


def import_session():
    """Open TikTok and let user log in manually to capture fresh session."""
    agent_id = 1
    profile_dir = BROWSER_PROFILES_DIR / f"agent_{agent_id}"
    profile_dir.mkdir(exist_ok=True)
    storage_path = profile_dir / "storage_state.json"

    log.info(f"Opening TikTok for manual login (Agent {agent_id})...")
    log.info(f"Session will be saved to: {storage_path}")

    playwright = sync_playwright().start()

    try:
        # Launch visible browser
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--window-size=1920,1080',
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        )

        page = context.new_page()

        # Navigate to TikTok
        log.info("Navigating to TikTok...")
        page.goto("https://www.tiktok.com")

        print("\n" + "="*70)
        print("MANUAL LOGIN INSTRUCTIONS")
        print("="*70)
        print("1. A browser window has opened showing TikTok")
        print("2. Click the 'Log in' button in the browser")
        print("3. Log in using your PASSKEY when prompted")
        print("4. Wait until you're logged in and can see your profile avatar")
        print("5. The browser will stay open for 60 seconds to complete login")
        print("="*70 + "\n")

        # Wait for user to log in (60 seconds)
        log.info("Waiting 60 seconds for you to log in...")
        for i in range(60, 0, -5):
            print(f"Saving session in {i} seconds... (complete your login now!)")
            time.sleep(5)

        # Check if logged in
        log.info("Checking if logged in...")
        time.sleep(2)

        # Look for profile indicators
        logged_in_selectors = [
            '[data-e2e="profile-icon"]',
            '[data-e2e="upload-icon"]',
            'a[href*="/upload"]',
        ]

        logged_in = False
        for selector in logged_in_selectors:
            try:
                if page.locator(selector).count() > 0:
                    logged_in = True
                    log.success(f"✓ Login confirmed! (found: {selector})")
                    break
            except:
                continue

        if not logged_in:
            log.warning("⚠ Could not confirm login - profile indicators not found")
            log.warning("Saving session anyway - it may not be authenticated")

        # Save session
        log.info("Saving session...")
        context.storage_state(path=str(storage_path))
        log.success(f"✓ Session saved to: {storage_path}")

        print("\n" + "="*70)
        if logged_in:
            print("SUCCESS! Authenticated session captured and saved.")
            print("You can now run the bot and it should work!")
        else:
            print("WARNING: Session saved but login could not be confirmed.")
            print("If the bot still shows 'Log in' button, please try again.")
        print("="*70 + "\n")

        # Keep browser open for a moment so user can see the result
        time.sleep(5)
        browser.close()
        playwright.stop()

        return logged_in

    except Exception as e:
        log.error(f"Error during session import: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close()
            playwright.stop()
        except:
            pass
        return False


if __name__ == "__main__":
    print("\nTikTok Session Import for Agent 1")
    print("=" * 70)
    print("This will open TikTok - log in with your passkey when prompted!")
    print("=" * 70 + "\n")

    success = import_session()

    if success:
        print("\n✓ Session import successful!")
        print("Run: python test_debug_comment.py")
    else:
        print("\n✗ Session import may have failed - check the logs")
