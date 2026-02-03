#!/usr/bin/env python3
"""Test a single automated comment cycle with AI generation."""

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

console.print(f"[cyan]Testing automated comment cycle for agent '{agent.username}'[/cyan]")
console.print("[dim]This will:[/dim]")
console.print("[dim]  1. Login to TikTok[/dim]")
console.print("[dim]  2. Navigate to For You page[/dim]")
console.print("[dim]  3. Click into a video[/dim]")
console.print("[dim]  4. Extract video info[/dim]")
console.print("[dim]  5. Generate AI comment[/dim]")
console.print("[dim]  6. Post the comment[/dim]\n")

# Create bot
bot = TikTokBot(
    agent_id=agent.id,
    username=agent.username,
    password=password
)

try:
    # Login
    console.print("[yellow]Step 1: Logging in...[/yellow]")
    if not bot.login():
        console.print("[red]Login failed[/red]")
        exit(1)
    console.print("[green]✓ Logged in[/green]\n")

    # Navigate
    console.print("[yellow]Step 2: Navigating to For You page...[/yellow]")
    if not bot.navigate_to_for_you():
        console.print("[red]Navigation failed[/red]")
        exit(1)
    console.print("[green]✓ Navigated to For You[/green]\n")

    # Click into video
    console.print("[yellow]Step 3: Clicking into a video...[/yellow]")
    if not bot.click_into_video():
        console.print("[red]Could not click into video[/red]")
        exit(1)
    console.print("[green]✓ Opened video[/green]\n")

    # Extract video info
    console.print("[yellow]Step 4: Extracting video info...[/yellow]")
    video_info = bot.get_video_info()
    if not video_info:
        console.print("[red]Could not extract video info[/red]")
        exit(1)

    console.print(f"[cyan]Video URL:[/cyan] {video_info.get('url', 'N/A')}")
    console.print(f"[cyan]Creator:[/cyan] {video_info.get('creator', 'N/A')}")
    console.print(f"[cyan]Description:[/cyan] {video_info.get('description', 'N/A')[:100]}...\n")

    # Generate AI comment
    console.print("[yellow]Step 5: Generating AI comment...[/yellow]")
    comment = comment_generator.generate_comment(
        video_description=video_info.get("description", ""),
        creator_name=video_info.get("creator", ""),
        video_context="TikTok For You page video"
    )
    console.print(f"[cyan]Generated comment:[/cyan] {comment}\n")

    # Ask for confirmation
    if not console.input("[yellow]Post this comment? (y/n): [/yellow]").lower().startswith('y'):
        console.print("[yellow]Skipping comment posting[/yellow]")
        exit(0)

    # Post comment
    console.print("[yellow]Step 6: Posting comment...[/yellow]")
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

        console.print("[green]✓ Test complete! Automation is working![/green]")
    else:
        console.print("[red]Failed to post comment[/red]")

finally:
    bot._save_session()
    bot._close_browser()
