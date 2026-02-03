#!/usr/bin/env python3
"""Step-by-step comment posting with screenshots after every action."""

from src.bot.android import TikTokAndroidBot
import time

def main():
    print("📸 Step-by-Step Comment Test")
    print("=" * 60)

    bot = TikTokAndroidBot(device_id="emulator-5554")
    width, height = bot._get_screen_size()
    print(f"\nScreen size: {width}x{height}\n")

    # Launch TikTok
    print("STEP 1: Launching TikTok...")
    bot.launch_tiktok()
    time.sleep(5)
    bot.wait_for_feed()
    time.sleep(2)
    bot.take_screenshot("data/step_1_feed_ready.png")
    print("  ✓ Screenshot: step_1_feed_ready.png")
    input("  Press Enter to continue...")

    # Tap comment icon
    print("\nSTEP 2: Tapping comment icon...")
    comment_icon_x = int(width * 0.95)
    comment_icon_y = int(height * 0.70)
    print(f"  Coordinates: ({comment_icon_x}, {comment_icon_y})")
    bot._tap(comment_icon_x, comment_icon_y, add_randomness=False)
    time.sleep(3)
    bot.take_screenshot("data/step_2_comment_section_open.png")
    print("  ✓ Screenshot: step_2_comment_section_open.png")
    input("  Press Enter to continue...")

    # Tap on input field (need to find correct spot)
    print("\nSTEP 3: Tapping on input field...")
    print("  Testing different input field positions...")

    # Try tapping where "Add comment..." text should be
    input_field_x = int(width * 0.50)  # Center of screen
    input_field_y = int(height * 0.93)  # Bottom where input is
    print(f"  Attempt 1 - Center: ({input_field_x}, {input_field_y})")
    bot._tap(input_field_x, input_field_y, add_randomness=False)
    time.sleep(2)
    bot.take_screenshot("data/step_3_after_tap_field.png")
    print("  ✓ Screenshot: step_3_after_tap_field.png")
    input("  Check screenshot - did keyboard appear? Press Enter...")

    # Type text
    print("\nSTEP 4: Typing comment text...")
    test_text = "Great video"
    print(f"  Text: '{test_text}'")
    bot._type_text(test_text)
    time.sleep(2)
    bot.take_screenshot("data/step_4_after_typing.png")
    print("  ✓ Screenshot: step_4_after_typing.png")
    input("  Check screenshot - is text visible? Press Enter...")

    # Tap Post/Submit button
    print("\nSTEP 5: Tapping Post button (pink/red button)...")
    # Post button should be on the RIGHT side of the input field
    post_button_x = int(width * 0.90)  # Far right
    post_button_y = int(height * 0.93)  # Same level as input
    print(f"  Coordinates: ({post_button_x}, {post_button_y})")
    bot._tap(post_button_x, post_button_y, add_randomness=False)
    time.sleep(3)
    bot.take_screenshot("data/step_5_after_post.png")
    print("  ✓ Screenshot: step_5_after_post.png")

    print("\n" + "=" * 60)
    print("✓ All steps complete!")
    print("\nScreenshots saved:")
    print("  1. step_1_feed_ready.png - For You feed")
    print("  2. step_2_comment_section_open.png - After tapping comment icon")
    print("  3. step_3_after_tap_field.png - After tapping input field")
    print("  4. step_4_after_typing.png - After typing text")
    print("  5. step_5_after_post.png - After tapping Post button")

if __name__ == "__main__":
    main()
