#!/usr/bin/env python3
"""Test automated comment - posts without confirmation."""

from src.bot.tiktok_bot import TikTokBot
from src.ai.comment_generator import comment_generator
from src.database import db
from rich.console import Console

console = Console()

# Get agent
agent = db.get_agent(1)
if not agent:
    console.print("[red]Agent not found[/red]")
    exit(1)

password = db.get_agent_password(1)

console.print(f"[cyan]Testing automated comment for agent '{agent.username}'[/cyan]\n")

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

    # Navigate
    console.print("[yellow]Navigating to For You...[/yellow]")
    if not bot.navigate_to_for_you():
        console.print("[red]Navigation failed[/red]")
        exit(1)
    console.print("[green]✓ Navigated[/green]\n")

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

    console.print(f"[cyan]Video:[/cyan] {video_info.get('url', 'N/A')}")
    console.print(f"[cyan]Creator:[/cyan] {video_info.get('creator', 'N/A')}")
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
    console.print("[yellow]Posting comment...[/yellow]")
    if bot.post_comment(comment):
        console.print("[green]✓ Comment posted successfully![/green]\n")

        # Log to database
        db.log_comment(
            agent_id=agent.id,
            video_url=video_info.get("url", ""),
            comment_text=comment,
            status="posted",
            video_description=video_info.get("description", "")
        )
        db.increment_agent_comments(agent.id)

        console.print("[green]✓✓✓ TEST COMPLETE - AUTOMATION WORKING! ✓✓✓[/green]")
    else:
        console.print("[red]Failed to post comment[/red]")
        exit(1)

finally:
    bot._save_session()
    bot._close_browser()
