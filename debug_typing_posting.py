#!/usr/bin/env python3
"""Debug typing and posting after comment section is open."""

from src.bot.android import TikTokAndroidBot
import time

def main():
    print("🔍 Debug Typing & Posting")
    print("=" * 50)

    bot = TikTokAndroidBot(device_id="emulator-5554")

    # Launch TikTok
    print("\n[1] Launching TikTok...")
    bot.launch_tiktok()
    time.sleep(5)
    bot.wait_for_feed()
    time.sleep(2)

    # Get screen size
    width, height = bot._get_screen_size()
    print(f"\n[2] Screen size: {width}x{height}")

    # Step 1: Open comment section (we know this works)
    print("\n[3] Opening comment section...")
    comment_icon_x = int(width * 0.95)
    comment_icon_y = int(height * 0.70)
    print(f"    Tapping comment icon at ({comment_icon_x}, {comment_icon_y})")
    bot._tap(comment_icon_x, comment_icon_y, add_randomness=False)
    time.sleep(3)
    bot.take_screenshot("data/debug_typing_1_section_open.png")
    print("    ✓ Screenshot: debug_typing_1_section_open.png")

    # Step 2: Tap input field
    print("\n[4] Tapping comment input field...")
    comment_input_x = int(width * 0.4)
    comment_input_y = int(height * 0.93)
    print(f"    Coordinates: ({comment_input_x}, {comment_input_y})")
    print(f"    Position: {int((comment_input_x/width)*100)}% width, {int((comment_input_y/height)*100)}% height")
    bot._tap(comment_input_x, comment_input_y, add_randomness=False)
    time.sleep(2)
    bot.take_screenshot("data/debug_typing_2_after_tap_input.png")
    print("    ✓ Screenshot: debug_typing_2_after_tap_input.png")

    # Step 3: Type text
    print("\n[5] Typing comment text...")
    test_comment = "Testing comment"
    print(f"    Text: '{test_comment}'")
    bot._type_text(test_comment)
    time.sleep(2)
    bot.take_screenshot("data/debug_typing_3_after_typing.png")
    print("    ✓ Screenshot: debug_typing_3_after_typing.png")

    # Step 4: Tap Post button
    print("\n[6] Tapping Post button...")
    send_button_x = int(width * 0.88)
    send_button_y = int(height * 0.93)
    print(f"    Coordinates: ({send_button_x}, {send_button_y})")
    print(f"    Position: {int((send_button_x/width)*100)}% width, {int((send_button_y/height)*100)}% height")
    bot._tap(send_button_x, send_button_y, add_randomness=False)
    time.sleep(2)
    bot.take_screenshot("data/debug_typing_4_after_post.png")
    print("    ✓ Screenshot: debug_typing_4_after_post.png")

    print("\n" + "=" * 50)
    print("✓ Debug complete!")
    print("\nCheck these screenshots:")
    print("  1. debug_typing_1_section_open.png - Comment section just opened")
    print("  2. debug_typing_2_after_tap_input.png - After tapping input field")
    print("  3. debug_typing_3_after_typing.png - After typing text")
    print("  4. debug_typing_4_after_post.png - After tapping Post button")
    print("\nLook for:")
    print("  - Is keyboard visible in screenshot 2?")
    print("  - Is text visible in input field in screenshot 3?")
    print("  - Did comment post in screenshot 4?")

if __name__ == "__main__":
    main()
