#!/usr/bin/env python3
"""Test comment posting with browser kept open for debugging."""

from src.bot.tiktok_bot import TikTokBot
from src.ai.comment_generator import comment_generator
from src.database import db
from rich.console import Console
import time

console = Console()

# Get agent
agent = db.get_agent(1)
if not agent:
    console.print("[red]Agent not found[/red]")
    exit(1)

password = db.get_agent_password(1)

console.print(f"[cyan]Testing automated comment (DEBUG MODE - Browser will stay open)[/cyan]\n")

# Create bot
bot = TikTokBot(
    agent_id=agent.id,
    username=agent.username,
    password=password
)

try:
    # Login
    console.print("[yellow]Logging in...[/yellow]")
    if not bot.login():
        console.print("[red]Login failed[/red]")
        exit(1)
    console.print("[green]✓ Logged in[/green]\n")

    # Navigate to Explore for random videos
    console.print("[yellow]Navigating to Explore...[/yellow]")
    if not bot.navigate_to_explore():
        console.print("[red]Navigation failed[/red]")
        exit(1)
    console.print("[green]✓ Navigated to Explore[/green]\n")

    # Click into video
    console.print("[yellow]Opening video...[/yellow]")
    if not bot.click_into_video():
        console.print("[red]Could not open video[/red]")
        exit(1)
    console.print("[green]✓ Video opened[/green]\n")

    # Extract video info
    console.print("[yellow]Extracting video info...[/yellow]")
    video_info = bot.get_video_info()
    if not video_info:
        console.print("[red]Could not extract video info[/red]")
        exit(1)

    console.print(f"[cyan]Video:[/cyan] {video_info.get('video_url', 'N/A')}")
    console.print(f"[cyan]Description:[/cyan] {video_info.get('description', 'N/A')[:80]}...\n")

    # Generate AI comment
    console.print("[yellow]Generating AI comment...[/yellow]")
    comment = comment_generator.generate_comment(
        video_description=video_info.get("description", ""),
        creator_name=video_info.get("creator", ""),
        video_context="TikTok video"
    )
    console.print(f"[cyan]Comment:[/cyan] {comment}\n")

    # Post comment
    console.print("[yellow]Attempting to post comment...[/yellow]")
    console.print("[dim]Watch the browser window to see what happens...[/dim]\n")

    result = bot.post_comment(comment)

    if result:
        console.print("[green]✓ Bot reports comment posted successfully![/green]\n")
        console.print(f"[bold cyan]>>> Verify comment here: {video_info.get('video_url', 'N/A')}[/bold cyan]\n")
    else:
        console.print("[red]✗ Bot reports comment posting failed[/red]\n")
        console.print(f"[yellow]>>> Video URL: {video_info.get('video_url', 'N/A')}[/yellow]\n")

    # Log to database regardless
    db.log_comment(
        agent_id=agent.id,
        video_url=video_info.get("video_url", ""),
        comment_text=comment,
        status="posted" if result else "failed",
        video_description=video_info.get("description", "")
    )

    if result:
        db.increment_agent_comments(agent.id)

    console.print("\n[yellow]===== DEBUG MODE =====[/yellow]")
    console.print(f"[cyan]Current URL:[/cyan] {bot.page.url}")
    console.print(f"[cyan]Comment text:[/cyan] {comment}")
    console.print("\n[yellow]Browser will stay open for 30 seconds so you can inspect...[/yellow]")
    console.print("[dim]Check if the comment is visible on the page[/dim]")
    console.print("[dim]Look at the comment input area[/dim]")
    console.print("[dim]Check for any error messages[/dim]\n")

    # Keep browser open for inspection
    for i in range(30, 0, -1):
        console.print(f"[dim]Closing in {i} seconds...[/dim]", end="\r")
        time.sleep(1)

    console.print("\n\n[yellow]Closing browser...[/yellow]")

finally:
    bot._save_session()
    bot._close_browser()
    console.print("[green]Done![/green]")
