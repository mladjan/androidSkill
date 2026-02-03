#!/usr/bin/env python3
"""Fully automated comment posting test."""

from src.bot.android import TikTokAndroidBot
from src.ai.comment_generator import comment_generator
import time

def main():
    print("🤖 Automated Comment Posting Test")
    print("=" * 50)

    # Initialize bot
    print("\n[1] Initializing Android bot...")
    bot = TikTokAndroidBot(device_id="emulator-5554")
    print("    ✓ Bot initialized")

    # Launch TikTok
    print("\n[2] Launching TikTok...")
    bot.launch_tiktok()
    time.sleep(5)
    print("    ✓ TikTok launched")

    # Wait for feed
    print("\n[3] Waiting for For You feed...")
    bot.wait_for_feed()
    time.sleep(2)
    print("    ✓ For You feed ready")

    # Skip to next video
    print("\n[4] Skipping to next video...")
    bot.skip_to_next_video(1)
    time.sleep(2)
    print("    ✓ Skipped to next video")

    # Take screenshot before commenting
    print("\n[5] Taking before screenshot...")
    bot.take_screenshot("data/final_test_before.png")
    print("    ✓ Saved: data/final_test_before.png")

    # Generate comment
    print("\n[6] Generating AI comment...")
    comment = comment_generator.generate_comment(
        video_description="TikTok video",
        creator_name="creator",
        video_context="Trending video"
    )
    print(f"    Comment: {comment}")

    # Post comment
    print("\n[7] Posting comment...")
    print(f"    Using coordinates: 95% width, 70% height")
    success = bot.post_comment(comment)

    if success:
        print("    ✓ Comment posted successfully!")
    else:
        print("    ⚠️  Comment posting may have failed")

    # Take screenshot after commenting
    print("\n[8] Taking after screenshot...")
    time.sleep(3)
    bot.take_screenshot("data/final_test_after.png")
    print("    ✓ Saved: data/final_test_after.png")

    print("\n" + "=" * 50)
    print("✓ Test complete!")
    print("\nCheck screenshots:")
    print("  data/final_test_before.png - Before posting")
    print("  data/final_test_after.png - After posting")
    print("\nLook for the comment in the after screenshot!")

if __name__ == "__main__":
    main()
