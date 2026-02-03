#!/usr/bin/env python3
"""Debug TikTok page to see what elements are available."""

from src.bot.tiktok_bot import TikTokBot
from src.database import db
from rich.console import Console
import time

console = Console()

# Get agent
agent = db.get_agent(1)
password = db.get_agent_password(1)

console.print("[cyan]Debugging TikTok page structure...[/cyan]\n")

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

    # Navigate
    console.print("[yellow]Navigating to For You page...[/yellow]")
    if not bot.navigate_to_for_you():
        console.print("[red]Navigation failed[/red]")
        exit(1)

    console.print("[green]✓ On For You page[/green]\n")

    # Wait for page to load
    console.print("[yellow]Waiting for page to load...[/yellow]")
    bot.page.wait_for_timeout(5000)

    # Try to scroll down to see comments section
    console.print("[yellow]Scrolling down...[/yellow]")
    bot.page.evaluate("window.scrollBy(0, 500)")
    bot.page.wait_for_timeout(2000)

    # Take screenshot
    screenshot_path = "data/debug_screenshot.png"
    bot.page.screenshot(path=screenshot_path)
    console.print(f"[green]✓ Screenshot saved: {screenshot_path}[/green]\n")

    # Check for comment-related elements
    console.print("[cyan]Looking for comment elements...[/cyan]\n")

    selectors_to_check = [
        '[data-e2e="comment-input"]',
        '[placeholder*="Add comment"]',
        '[placeholder*="comment"]',
        'div[contenteditable="true"]',
        '[data-e2e="comment-panel"]',
        '[data-e2e="browse-comment"]',
        'input[type="text"]',
        'textarea',
        '.comment-input',
        '#comment-input',
    ]

    for selector in selectors_to_check:
        count = bot.page.locator(selector).count()
        if count > 0:
            console.print(f"  [green]✓[/green] Found {count}x: {selector}")
            # Try to get element attributes
            try:
                elem = bot.page.locator(selector).first
                if elem.is_visible():
                    console.print(f"    [dim]Visible: Yes[/dim]")
                else:
                    console.print(f"    [dim]Visible: No (might need scroll)[/dim]")
            except:
                pass
        else:
            console.print(f"  [dim]✗[/dim] Not found: {selector}")

    console.print("\n[cyan]Current URL:[/cyan]")
    console.print(f"  {bot.page.url}")

    console.print("\n[cyan]Page title:[/cyan]")
    console.print(f"  {bot.page.title()}")

    # Check if we're on a video page
    console.print("\n[yellow]Checking page type...[/yellow]")
    if "/video/" in bot.page.url:
        console.print("[green]✓ On a video page (comments should be available)[/green]")
    elif bot.page.url.endswith("/foryou") or "foryou" in bot.page.url:
        console.print("[yellow]⚠ On For You feed (need to click into a video first)[/yellow]")
    else:
        console.print(f"[yellow]⚠ Unknown page type[/yellow]")

    console.print("\n[dim]Browser will stay open for 10 seconds so you can inspect...[/dim]")
    time.sleep(10)

finally:
    bot._save_session()
    bot._close_browser()
    console.print("\n[green]Debug complete![/green]")
