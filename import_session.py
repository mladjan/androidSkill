#!/usr/bin/env python3
"""Import existing TikTok session from browser cookies.

Use this if your account uses passkey-only authentication.
"""

import json
import click
from pathlib import Path
from src.config import BROWSER_PROFILES_DIR
from src.database import db
from rich.console import Console

console = Console()


@click.command()
@click.argument("agent_id", type=int)
@click.argument("cookies_file", type=click.Path(exists=True))
def import_session(agent_id: int, cookies_file: str):
    """Import browser session for agent.

    Usage:
        1. Login to TikTok in your browser (using passkey)
        2. Export cookies as JSON using browser extension
        3. Run: python import_session.py 1 cookies.json
    """
    # Load agent
    agent = db.get_agent(agent_id)
    if not agent:
        console.print(f"[red]Agent {agent_id} not found[/red]")
        return

    console.print(f"[cyan]Importing session for agent '{agent.username}'...[/cyan]")

    # Load cookies from file
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)

    # Verify it's TikTok cookies
    tiktok_cookies = [c for c in cookies if 'tiktok.com' in c.get('domain', '')]
    if not tiktok_cookies:
        console.print("[red]Error: No TikTok cookies found in file[/red]")
        return

    console.print(f"[green]Found {len(tiktok_cookies)} TikTok cookies[/green]")

    # Convert cookies to Playwright format
    playwright_cookies = []
    for cookie in tiktok_cookies:
        # Convert sameSite values to Playwright-compatible format
        same_site = cookie.get('sameSite', 'Lax')
        if same_site == 'no_restriction':
            same_site = 'None'
        elif same_site == 'unspecified':
            same_site = 'Lax'
        elif same_site not in ['Strict', 'Lax', 'None']:
            same_site = 'Lax'

        playwright_cookie = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie['path'],
            'sameSite': same_site,
        }

        # Add optional fields
        if 'expires' in cookie:
            playwright_cookie['expires'] = cookie['expires']
        elif 'expirationDate' in cookie:
            playwright_cookie['expires'] = cookie['expirationDate']

        if 'httpOnly' in cookie:
            playwright_cookie['httpOnly'] = cookie['httpOnly']

        if 'secure' in cookie:
            playwright_cookie['secure'] = cookie['secure']

        playwright_cookies.append(playwright_cookie)

    console.print(f"[cyan]Converted {len(playwright_cookies)} cookies to Playwright format[/cyan]")

    # Create storage state format for Playwright
    storage_state = {
        "cookies": playwright_cookies,
        "origins": [
            {
                "origin": "https://www.tiktok.com",
                "localStorage": []
            }
        ]
    }

    # Save to agent's profile directory
    profile_dir = BROWSER_PROFILES_DIR / f"agent_{agent_id}"
    profile_dir.mkdir(exist_ok=True)

    storage_path = profile_dir / "storage_state.json"
    with open(storage_path, 'w') as f:
        json.dump(storage_state, f, indent=2)

    console.print(f"[green]✓[/green] Session imported successfully!")
    console.print(f"[dim]Saved to: {storage_path}[/dim]")
    console.print("\n[yellow]Note:[/yellow] This session will expire eventually.")
    console.print("You may need to re-import periodically.")

    # Update agent status
    db.update_agent_status(agent_id, "idle")

    console.print("\n[cyan]Test the session:[/cyan]")
    console.print(f"python main.py agent test {agent_id}")


if __name__ == "__main__":
    import_session()
