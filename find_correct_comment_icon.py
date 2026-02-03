#!/usr/bin/env python3
"""Find the ACTUAL comment icon by testing multiple Y positions."""

from src.bot.android import TikTokAndroidBot
import time

def main():
    print("🔍 Finding Correct Comment Icon Position")
    print("=" * 60)

    bot = TikTokAndroidBot(device_id="emulator-5554")
    width, height = bot._get_screen_size()
    print(f"Screen size: {width}x{height}\n")

    # Launch TikTok
    print("Setting up...")
    bot.launch_tiktok()
    time.sleep(5)
    bot.wait_for_feed()
    time.sleep(2)
    bot.take_screenshot("data/icon_test_0_feed.png")
    print("✓ Ready\n")

    # Test positions from 50% to 75% height in 5% increments
    x_right = int(width * 0.95)

    test_heights = [
        (0.50, "50% - Upper area"),
        (0.55, "55% - Upper-middle"),
        (0.60, "60% - Middle"),
        (0.65, "65% - Lower-middle"),
        (0.70, "70% - Lower"),
        (0.75, "75% - Bottom area"),
    ]

    for i, (height_pct, description) in enumerate(test_heights, 1):
        y_pos = int(height * height_pct)

        print(f"Test {i}/6: {description}")
        print(f"  Position: ({x_right}, {y_pos})")
        print(f"  Tapping...")

        bot._tap(x_right, y_pos, add_randomness=False)
        time.sleep(3)

        screenshot_name = f"data/icon_test_{i}_{int(height_pct*100)}pct.png"
        bot.take_screenshot(screenshot_name)
        print(f"  Screenshot: {screenshot_name}")

        # Check if comment section opened by looking for comment drawer
        print(f"  CHECK: Did COMMENT SECTION with existing comments appear?\n")

        # Go back
        bot.go_back()
        time.sleep(2)

    print("=" * 60)
    print("Review screenshots to find which one opened COMMENT SECTION:")
    for i, (height_pct, description) in enumerate(test_heights, 1):
        print(f"  {i}. icon_test_{i}_{int(height_pct*100)}pct.png - {description}")
    print("\nLook for the screenshot that shows:")
    print("  - Comment drawer from bottom")
    print("  - List of existing comments")
    print("  - 'Add comment...' input field at bottom")

if __name__ == "__main__":
    main()
