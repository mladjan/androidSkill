"""Script to import a fresh TikTok session by logging in manually.

This script will open TikTok in a browser, allow you to log in manually with your passkey,
and then save the authenticated session for the bot to use.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from src.config import BROWSER_PROFILES_DIR
from src.logger import log


def import_fresh_session(agent_id: int = 1):
    """Open TikTok and let user log in manually to capture fresh session.

    Args:
        agent_id: ID of the agent to import session for
    """
    profile_dir = BROWSER_PROFILES_DIR / f"agent_{agent_id}"
    profile_dir.mkdir(exist_ok=True)
    storage_path = profile_dir / "storage_state.json"

    log.info(f"Opening TikTok for manual login...")
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

        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("1. Click 'Log in' button in the browser")
        print("2. Log in using your passkey or any method")
        print("3. Wait until you see your profile avatar in the top right")
        print("4. Once logged in, press ENTER here to save the session...")
        print("="*60 + "\n")

        # Wait for user to log in
        input("Press ENTER after you've logged in successfully...")

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
                    log.info(f"✓ Login confirmed (found: {selector})")
                    break
            except:
                continue

        if not logged_in:
            log.warning("⚠ Could not confirm login - profile indicators not found")
            response = input("Do you want to save the session anyway? (y/n): ")
            if response.lower() != 'y':
                log.info("Session not saved")
                browser.close()
                playwright.stop()
                return False

        # Save session
        log.info("Saving session...")
        context.storage_state(path=str(storage_path))
        log.success(f"✓ Session saved to: {storage_path}")

        print("\n" + "="*60)
        print("SUCCESS! Session captured and saved.")
        print("You can now close the browser and run your bot.")
        print("="*60 + "\n")

        # Keep browser open for a moment
        time.sleep(2)
        browser.close()
        playwright.stop()

        return True

    except Exception as e:
        log.error(f"Error during session import: {e}")
        try:
            browser.close()
            playwright.stop()
        except:
            pass
        return False


if __name__ == "__main__":
    print("\nTikTok Session Import")
    print("=" * 60)
    print("This script will open TikTok in a browser.")
    print("You will log in manually, and we'll save your authenticated session.")
    print("=" * 60 + "\n")

    agent_id = input("Enter agent ID (default: 1): ").strip() or "1"
    agent_id = int(agent_id)

    success = import_fresh_session(agent_id)

    if success:
        print("\n✓ Session import successful!")
        print("You can now run your bot with the authenticated session.")
    else:
        print("\n✗ Session import failed")
        print("Please try again")
