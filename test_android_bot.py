#!/usr/bin/env python3
"""Test Android TikTok bot."""

from src.bot.android import TikTokAndroidBot
from src.ai.comment_generator import comment_generator
from rich.console import Console
import time

console = Console()

def main():
    console.print("[cyan]🤖 Android TikTok Bot Test[/cyan]\n")

    # Initialize bot
    try:
        bot = TikTokAndroidBot(device_id="emulator-5554")
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize bot: {e}[/red]")
        return

    # Check if TikTok is installed
    if not bot.is_tiktok_installed():
        console.print("[yellow]TikTok is not installed on the emulator.[/yellow]")
        console.print("[yellow]You need to install TikTok manually or provide an APK.[/yellow]")
        console.print("\n[dim]To install TikTok:[/dim]")
        console.print("[dim]1. Download TikTok APK from APKMirror or similar[/dim]")
        console.print("[dim]2. Run: adb install -r tiktok.apk[/dim]")
        console.print("[dim]3. Open TikTok on emulator and log in manually[/dim]")
        console.print("[dim]4. Re-run this script[/dim]")
        return

    console.print("[green]✓ TikTok is installed[/green]\n")

    # Launch TikTok
    console.print("[yellow]Launching TikTok...[/yellow]")
    if not bot.launch_tiktok():
        console.print("[red]✗ Failed to launch TikTok[/red]")
        return

    console.print("[green]✓ TikTok launched[/green]\n")

    # Wait for feed to load
    console.print("[yellow]Waiting for For You feed...[/yellow]")
    bot.wait_for_feed()

    # Wait for manual setup if needed
    console.print("\n[yellow]⏱️  Please check the emulator:[/yellow]")
    console.print("[dim]- If TikTok asks for permissions, grant them[/dim]")
    console.print("[dim]- If you're not logged in, log in manually[/dim]")
    console.print("[dim]- You should see a video playing on For You feed[/dim]")
    input("\n[cyan]Press Enter when ready to continue...[/cyan]")

    # Optionally skip a video or two
    console.print("\n[yellow]Skipping to next video...[/yellow]")
    bot.skip_to_next_video(1)
    time.sleep(2)

    # Take screenshot before commenting
    console.print("[yellow]Taking screenshot...[/yellow]")
    bot.take_screenshot("data/android_before_comment.png")

    # Generate AI comment
    console.print("\n[yellow]Generating AI comment...[/yellow]")
    comment = comment_generator.generate_comment(
        video_description="TikTok video",
        creator_name="creator",
        video_context="Trending video"
    )
    console.print(f"[cyan]Comment:[/cyan] {comment}\n")

    # Post comment
    console.print("[yellow]Posting comment...[/yellow]")
    success = bot.post_comment(comment)

    if success:
        console.print("[green]✓ Comment posted![/green]\n")
    else:
        console.print("[red]✗ Comment posting may have failed[/red]\n")

    # Take screenshot after commenting
    time.sleep(2)
    bot.take_screenshot("data/android_after_comment.png")

    console.print("[yellow]📸 Screenshots saved:[/yellow]")
    console.print("[dim]- data/android_before_comment.png[/dim]")
    console.print("[dim]- data/android_after_comment.png[/dim]\n")

    console.print("[green]✓ Test complete![/green]")
    console.print("\n[yellow]The emulator will stay open for you to verify.[/yellow]")
    console.print("[dim]Check if the comment appears in the video's comment section.[/dim]")

if __name__ == "__main__":
    main()
