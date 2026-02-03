#!/usr/bin/env python3
"""Step-by-step comment posting with screenshots after every action - AUTOMATED."""

from src.bot.android import TikTokAndroidBot
import time

def main():
    print("📸 Step-by-Step Comment Test (Automated)")
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
    print("  ✓ Screenshot: step_1_feed_ready.png\n")

    # Tap comment icon
    print("STEP 2: Tapping comment icon...")
    comment_icon_x = int(width * 0.95)
    comment_icon_y = int(height * 0.70)
    print(f"  Coordinates: ({comment_icon_x}, {comment_icon_y}) = 95% width, 70% height")
    bot._tap(comment_icon_x, comment_icon_y, add_randomness=False)
    time.sleep(3)
    bot.take_screenshot("data/step_2_comment_section_open.png")
    print("  ✓ Screenshot: step_2_comment_section_open.png\n")

    # Tap on input field - try center position
    print("STEP 3: Tapping on input field...")
    input_field_x = int(width * 0.50)  # Center
    input_field_y = int(height * 0.93)  # Bottom
    print(f"  Coordinates: ({input_field_x}, {input_field_y}) = 50% width, 93% height")
    bot._tap(input_field_x, input_field_y, add_randomness=False)
    time.sleep(2)
    bot.take_screenshot("data/step_3_after_tap_field.png")
    print("  ✓ Screenshot: step_3_after_tap_field.png")
    print("  CHECK: Did keyboard appear? Or did stylus popup appear?\n")

    # Type text
    print("STEP 4: Typing comment text...")
    test_text = "Great video"
    print(f"  Text: '{test_text}'")
    bot._type_text(test_text)
    time.sleep(2)
    bot.take_screenshot("data/step_4_after_typing.png")
    print("  ✓ Screenshot: step_4_after_typing.png")
    print("  CHECK: Is text visible in input field?\n")

    # Tap Post/Submit button (pink/red)
    print("STEP 5: Tapping Post button (pink/red button on right)...")
    post_button_x = int(width * 0.90)  # Far right
    post_button_y = int(height * 0.93)  # Same level as input
    print(f"  Coordinates: ({post_button_x}, {post_button_y}) = 90% width, 93% height")
    bot._tap(post_button_x, post_button_y, add_randomness=False)
    time.sleep(3)
    bot.take_screenshot("data/step_5_after_post.png")
    print("  ✓ Screenshot: step_5_after_post.png")
    print("  CHECK: Did comment post? Did we go back to video?\n")

    print("=" * 60)
    print("✓ All steps complete!")
    print("\nReview screenshots to identify issues:")
    print("  1. step_1_feed_ready.png - For You feed")
    print("  2. step_2_comment_section_open.png - Comment section open?")
    print("  3. step_3_after_tap_field.png - Keyboard visible or stylus popup?")
    print("  4. step_4_after_typing.png - Text in field?")
    print("  5. step_5_after_post.png - Comment posted?")

if __name__ == "__main__":
    main()
