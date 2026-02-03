#!/usr/bin/env python3
"""Debug Android bot - Take screenshots at each step to identify correct coordinates."""

from src.bot.android import TikTokAndroidBot
from rich.console import Console
import time

console = Console()

def main():
    console.print("[cyan]🐛 Android Bot Debug - Screenshot Every Step[/cyan]\n")

    try:
        bot = TikTokAndroidBot(device_id="emulator-5554")
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize: {e}[/red]")
        return

    if not bot.is_tiktok_installed():
        console.print("[red]TikTok not installed. Please install it first.[/red]")
        return

    console.print("[green]✓ TikTok is installed[/green]\n")

    # Step 1: Launch TikTok
    console.print("[yellow]Step 1: Launching TikTok...[/yellow]")
    bot.launch_tiktok()
    time.sleep(5)
    bot.take_screenshot("data/debug_step1_launched.png")
    console.print("[green]Screenshot: debug_step1_launched.png[/green]\n")

    input("[cyan]Press Enter to continue...[/cyan]")

    # Step 2: Wait for feed
    console.print("[yellow]Step 2: Waiting for For You feed...[/yellow]")
    bot.wait_for_feed()
    bot.take_screenshot("data/debug_step2_feed.png")
    console.print("[green]Screenshot: debug_step2_feed.png[/green]\n")

    input("[cyan]Press Enter to try tapping comment icon...[/cyan]")

    # Step 3: Get screen size and show where we'll tap
    width, height = bot._get_screen_size()
    console.print(f"[yellow]Screen size: {width}x{height}[/yellow]")

    # Calculate where we think the comment icon is
    comment_icon_x = int(width * 0.93)
    comment_icon_y = int(height * 0.60)
    console.print(f"[yellow]Will tap at: ({comment_icon_x}, {comment_icon_y})[/yellow]\n")

    # Step 4: Tap where we think comment icon is
    console.print("[yellow]Step 3: Tapping comment icon position...[/yellow]")
    bot._tap(comment_icon_x, comment_icon_y)
    time.sleep(3)
    bot.take_screenshot("data/debug_step3_after_tap.png")
    console.print("[green]Screenshot: debug_step3_after_tap.png[/green]\n")

    console.print("[yellow]Check the screenshot - what opened?[/yellow]")
    input("[cyan]Press Enter to continue...[/cyan]")

    # Step 5: Try pressing back to close whatever opened
    console.print("[yellow]Step 4: Pressing back button...[/yellow]")
    bot.go_back()
    time.sleep(2)
    bot.take_screenshot("data/debug_step4_after_back.png")
    console.print("[green]Screenshot: debug_step4_after_back.png[/green]\n")

    # Step 6: Let's try different coordinates
    console.print("[yellow]Let's try different Y coordinate (lower on screen)...[/yellow]")
    input("[cyan]Press Enter to try...[/cyan]")

    comment_icon_x = int(width * 0.93)
    comment_icon_y = int(height * 0.70)  # Lower
    console.print(f"[yellow]Trying: ({comment_icon_x}, {comment_icon_y})[/yellow]")

    bot._tap(comment_icon_x, comment_icon_y)
    time.sleep(3)
    bot.take_screenshot("data/debug_step5_try2.png")
    console.print("[green]Screenshot: debug_step5_try2.png[/green]\n")

    input("[cyan]Press Enter to try another position...[/cyan]")
    bot.go_back()
    time.sleep(2)

    # Step 7: Try even lower
    comment_icon_y = int(height * 0.55)  # Higher up
    console.print(f"[yellow]Trying: ({comment_icon_x}, {comment_icon_y})[/yellow]")

    bot._tap(comment_icon_x, comment_icon_y)
    time.sleep(3)
    bot.take_screenshot("data/debug_step6_try3.png")
    console.print("[green]Screenshot: debug_step6_try3.png[/green]\n")

    console.print("\n[yellow]===== DEBUG COMPLETE =====[/yellow]")
    console.print("[cyan]Check these screenshots in data/ folder:[/cyan]")
    console.print("- debug_step1_launched.png - TikTok just opened")
    console.print("- debug_step2_feed.png - For You feed ready")
    console.print("- debug_step3_after_tap.png - After first tap attempt")
    console.print("- debug_step4_after_back.png - After pressing back")
    console.print("- debug_step5_try2.png - Second tap attempt")
    console.print("- debug_step6_try3.png - Third tap attempt")
    console.print("\n[yellow]Look at these screenshots and tell me which one opened the comment section![/yellow]")

if __name__ == "__main__":
    main()
