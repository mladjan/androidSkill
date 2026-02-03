#!/usr/bin/env python3
"""Automated coordinate testing - no user input required."""

from src.bot.android import TikTokAndroidBot
import time

def main():
    print("🤖 Automated Coordinate Test")
    print("=" * 50)

    bot = TikTokAndroidBot(device_id="emulator-5554")

    # Launch TikTok
    print("\n[1] Launching TikTok...")
    bot.launch_tiktok()
    time.sleep(5)

    # Wait for feed
    print("[2] Waiting for For You feed...")
    bot.wait_for_feed()
    time.sleep(2)

    # Take initial screenshot
    print("[3] Taking initial screenshot...")
    bot.take_screenshot("data/auto_test_0_initial.png")
    print("    Saved: data/auto_test_0_initial.png")

    # Get screen size
    width, height = bot._get_screen_size()
    print(f"\n[4] Screen size: {width}x{height}")

    # Test different Y positions on right side
    x_right = int(width * 0.95)  # Far right edge

    test_positions = [
        (0.45, "top_right"),
        (0.55, "upper_middle_right"),
        (0.60, "middle_right"),
        (0.65, "lower_middle_right"),
        (0.70, "lower_right"),
        (0.75, "bottom_right"),
    ]

    print("\n[5] Testing coordinates...")
    for i, (y_percent, name) in enumerate(test_positions, 1):
        y_pos = int(height * y_percent)

        print(f"\n    Test {i}/6: {name}")
        print(f"    Coordinates: ({x_right}, {y_pos})")
        print(f"    Position: {int((x_right/width)*100)}% width, {int(y_percent*100)}% height")

        # Tap
        print(f"    Tapping...")
        bot._tap(x_right, y_pos, add_randomness=False)
        time.sleep(3)

        # Take screenshot
        screenshot_name = f"data/auto_test_{i}_{name}.png"
        bot.take_screenshot(screenshot_name)
        print(f"    Screenshot saved: {screenshot_name}")

        # Press back to close whatever opened
        print(f"    Pressing back...")
        bot.go_back()
        time.sleep(2)

    print("\n" + "=" * 50)
    print("✓ All tests complete!")
    print("\nCheck these screenshots:")
    print("  data/auto_test_0_initial.png - Initial For You feed")
    for i, (y_percent, name) in enumerate(test_positions, 1):
        print(f"  data/auto_test_{i}_{name}.png - After tapping {int(y_percent*100)}% height")

    print("\nLook for which screenshot shows the COMMENT SECTION open!")
    print("That's the correct Y coordinate to use.")

if __name__ == "__main__":
    main()
