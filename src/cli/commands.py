"""CLI commands implementation."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.database import db
from src.config import config, BASE_DIR
from src.logger import log

console = Console()


# ========== Agent Management Commands ==========

@click.group(name="agent")
def agent_group():
    """Manage TikTok agents (accounts)."""
    pass


@agent_group.command(name="add")
def agent_add():
    """Add a new TikTok agent."""
    console.print(Panel.fit("Add New TikTok Agent", style="bold cyan"))

    username = click.prompt("TikTok username", type=str)
    password = click.prompt("TikTok password", type=str, hide_input=True)
    password_confirm = click.prompt("Confirm password", type=str, hide_input=True)

    if password != password_confirm:
        console.print("[red]Passwords do not match![/red]")
        return

    email = click.prompt("Email (optional, press Enter to skip)", type=str, default="", show_default=False)

    try:
        agent = db.create_agent(username=username, password=password, email=email or None)
        console.print(f"[green]✓[/green] Agent '{agent.username}' added successfully (ID: {agent.id})")
        log.info(f"Agent created: {agent.username} (ID: {agent.id})")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Failed to add agent: {e}[/red]")
        log.exception("Failed to add agent")


@agent_group.command(name="list")
def agent_list():
    """List all agents."""
    agents = db.list_agents()

    if not agents:
        console.print("[yellow]No agents found. Add one with 'python main.py agent add'[/yellow]")
        return

    table = Table(title="TikTok Agents", box=box.ROUNDED)
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Username", style="white")
    table.add_column("Email", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Today/Total", justify="center", style="yellow")
    table.add_column("Last Activity", style="dim")

    for agent in agents:
        # Status with color
        status_map = {
            "idle": "[green]🟢 Idle[/green]",
            "active": "[blue]🔵 Active[/blue]",
            "error": "[red]🔴 Error[/red]",
            "banned": "[red]🚫 Banned[/red]"
        }
        status = status_map.get(agent.status, agent.status)

        # Last activity
        last_activity = agent.last_activity.strftime("%Y-%m-%d %H:%M") if agent.last_activity else "Never"

        table.add_row(
            str(agent.id),
            agent.username,
            agent.email or "-",
            status,
            f"{agent.comments_today}/{agent.comments_total}",
            last_activity
        )

    console.print(table)


@agent_group.command(name="remove")
@click.argument("agent_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to remove this agent?")
def agent_remove(agent_id: int):
    """Remove an agent by ID."""
    if db.delete_agent(agent_id):
        console.print(f"[green]✓[/green] Agent {agent_id} removed successfully")
        log.info(f"Agent {agent_id} removed")
    else:
        console.print(f"[red]Agent {agent_id} not found[/red]")


@agent_group.command(name="test")
@click.argument("agent_id", type=int)
def agent_test(agent_id: int):
    """Test agent login with TikTok bot."""
    from src.bot.tiktok_bot import TikTokBot

    agent = db.get_agent(agent_id)
    if not agent:
        console.print(f"[red]Agent {agent_id} not found[/red]")
        return

    console.print(f"[yellow]Testing login for agent '{agent.username}'...[/yellow]")
    console.print("[dim]This will open a browser and attempt to login to TikTok[/dim]\n")

    # Get decrypted password
    password = db.get_agent_password(agent_id)
    if not password:
        console.print(f"[red]Could not decrypt password for agent {agent_id}[/red]")
        return

    try:
        # Create bot instance
        bot = TikTokBot(agent_id=agent_id, username=agent.username, password=password)

        # Attempt login
        console.print("[cyan]Launching browser and attempting login...[/cyan]")
        success = bot.login()

        if success:
            console.print(f"[green]✓[/green] Login successful for '{agent.username}'!")
            db.update_agent_status(agent_id, "idle")
        else:
            console.print(f"[red]✗[/red] Login failed for '{agent.username}'")
            console.print("[yellow]Check the logs for more details[/yellow]")
            db.update_agent_status(agent_id, "error", "Login test failed")

    except Exception as e:
        console.print(f"[red]Error during login test: {e}[/red]")
        log.exception("Agent test failed")
        db.update_agent_status(agent_id, "error", str(e))


# ========== Configuration Commands ==========

@click.group(name="config")
def config_group():
    """Manage bot configuration."""
    pass


@config_group.command(name="show")
def config_show():
    """Show current configuration."""
    table = Table(title="Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    # Show key settings
    table.add_row("AI API Key", "***" + config.OPENAI_API_KEY[-8:] if config.OPENAI_API_KEY else "[red]Not Set[/red]")
    table.add_row("AI Base URL", config.OPENAI_BASE_URL)
    table.add_row("AI Model", config.OPENAI_MODEL)
    table.add_row("Comments Per Day", str(config.COMMENTS_PER_DAY))
    table.add_row("Min Delay (minutes)", str(config.MIN_DELAY_MINUTES))
    table.add_row("Max Delay (minutes)", str(config.MAX_DELAY_MINUTES))
    table.add_row("Headless Mode", "Yes" if config.HEADLESS else "No")
    table.add_row("Database", str(config.DATABASE_URL))
    table.add_row("Log Level", config.LOG_LEVEL)

    console.print(table)

    # Validate and show warnings
    errors = config.validate()
    if errors:
        console.print("\n[yellow]⚠ Configuration Issues:[/yellow]")
        for error in errors:
            console.print(f"  • {error}")


@config_group.command(name="set-api-key")
@click.argument("api_key", type=str)
def config_set_api_key(api_key: str):
    """Set AI API key (OpenRouter or OpenAI)."""
    env_file = BASE_DIR / ".env"

    # Read existing .env or create new
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()

        # Update or add OPENAI_API_KEY
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("OPENAI_API_KEY="):
                lines[i] = f"OPENAI_API_KEY={api_key}\n"
                updated = True
                break

        if not updated:
            lines.append(f"\nOPENAI_API_KEY={api_key}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)
    else:
        with open(env_file, "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")

    console.print("[green]✓[/green] AI API key saved to .env")
    console.print("[dim]Restart the application to apply changes[/dim]")


@config_group.command(name="set-model")
@click.argument("model", type=str)
def config_set_model(model: str):
    """Set AI model (e.g., meta-llama/llama-3.3-70b-instruct:free)."""
    env_file = BASE_DIR / ".env"

    # Read existing .env or create new
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()

        # Update or add OPENAI_MODEL
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("OPENAI_MODEL="):
                lines[i] = f"OPENAI_MODEL={model}\n"
                updated = True
                break

        if not updated:
            lines.append(f"\nOPENAI_MODEL={model}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)
    else:
        with open(env_file, "w") as f:
            f.write(f"OPENAI_MODEL={model}\n")

    console.print(f"[green]✓[/green] AI model set to {model}")
    console.print("[dim]Restart the application to apply changes[/dim]")


@config_group.command(name="set-daily-limit")
@click.argument("limit", type=int)
def config_set_daily_limit(limit: int):
    """Set comments per day limit."""
    if limit < 1 or limit > 50:
        console.print("[red]Limit must be between 1 and 50[/red]")
        return

    env_file = BASE_DIR / ".env"

    # Similar logic to set-openai-key
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            if line.startswith("COMMENTS_PER_DAY="):
                lines[i] = f"COMMENTS_PER_DAY={limit}\n"
                updated = True
                break

        if not updated:
            lines.append(f"\nCOMMENTS_PER_DAY={limit}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)
    else:
        with open(env_file, "w") as f:
            f.write(f"COMMENTS_PER_DAY={limit}\n")

    console.print(f"[green]✓[/green] Daily comment limit set to {limit}")
    console.print("[dim]Restart the application to apply changes[/dim]")


# ========== Control Commands ==========

@click.command(name="start")
@click.option("--daemon", "-d", is_flag=True, help="Run in background (daemon mode)")
def start_command(daemon: bool):
    """Start the automation scheduler."""
    from src.scheduler import bot_scheduler

    if bot_scheduler.is_running:
        console.print("[yellow]Scheduler is already running[/yellow]")
        return

    console.print("[cyan]Starting SocialBot automation...[/cyan]")

    # Check for active agents
    agents = db.get_all_agents()
    active_agents = [a for a in agents if a.status in ["idle", "active"]]

    if not active_agents:
        console.print("[red]No active agents found. Add an agent first:[/red]")
        console.print("  python main.py agent add")
        return

    console.print(f"Found {len(active_agents)} active agent(s)")

    # Start scheduler
    try:
        bot_scheduler.start()

        # Show status
        status = bot_scheduler.get_status()

        console.print(f"\n[green]✓[/green] Scheduler started successfully!")
        console.print(f"[dim]Active agents: {status['active_agents']}")
        console.print(f"[dim]Scheduled jobs: {status['scheduled_jobs']}")

        console.print("\n[cyan]Agents:[/cyan]")
        for agent_info in status['agents']:
            console.print(f"  • {agent_info['username']} - Next run: {agent_info['next_run']}")

        if daemon:
            console.print("\n[yellow]Running in background. Use 'python main.py stop' to stop.[/yellow]")
            console.print("[dim]Logs: tail -f data/logs/bot.log[/dim]")

            # Keep process running
            import signal
            import time

            def signal_handler(sig, frame):
                console.print("\n[yellow]Stopping scheduler...[/yellow]")
                bot_scheduler.stop()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            console.print("\n[green]Press Ctrl+C to stop[/green]\n")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping scheduler...[/yellow]")
                bot_scheduler.stop()

        else:
            console.print("\n[yellow]Note:[/yellow] Scheduler is running in the current process.")
            console.print("Keep this terminal open or run with --daemon flag.")
            console.print("\nView status: python main.py status")
            console.print("View logs: tail -f data/logs/bot.log")

    except Exception as e:
        console.print(f"[red]Failed to start scheduler: {e}[/red]")
        log.error(f"Error starting scheduler: {e}")


@click.command(name="stop")
def stop_command():
    """Stop the automation scheduler."""
    from src.scheduler import bot_scheduler

    if not bot_scheduler.is_running:
        console.print("[yellow]Scheduler is not running[/yellow]")
        return

    console.print("[cyan]Stopping SocialBot automation...[/cyan]")

    try:
        bot_scheduler.stop()
        console.print("[green]✓[/green] Scheduler stopped successfully")
    except Exception as e:
        console.print(f"[red]Failed to stop scheduler: {e}[/red]")
        log.error(f"Error stopping scheduler: {e}")


@click.command(name="status")
def status_command():
    """Show live status dashboard."""
    from src.scheduler import bot_scheduler

    status = bot_scheduler.get_status()

    # Create status panel
    if status['running']:
        status_text = "[green]● Running[/green]"
    else:
        status_text = "[red]● Stopped[/red]"

    panel_content = f"""
[cyan]Scheduler Status:[/cyan]  {status_text}
[cyan]Total Agents:[/cyan]      {status['total_agents']}
[cyan]Active Agents:[/cyan]     {status['active_agents']}
[cyan]Scheduled Jobs:[/cyan]    {status['scheduled_jobs']}
    """

    console.print(Panel(panel_content, title="SocialBot Status", border_style="cyan"))

    # Show agent details
    if status['agents']:
        table = Table(title="Active Agents", box=box.ROUNDED)
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Username", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Comments Today", justify="center")
        table.add_column("Next Run", style="yellow")

        for agent_info in status['agents']:
            status_icon = {
                "idle": "[green]🟢 Idle[/green]",
                "active": "[blue]🔵 Active[/blue]",
                "error": "[red]🔴 Error[/red]",
                "banned": "[red]⛔ Banned[/red]"
            }.get(agent_info['status'], agent_info['status'])

            table.add_row(
                str(agent_info['id']),
                agent_info['username'],
                status_icon,
                f"{agent_info['comments_today']}/{config.COMMENTS_PER_DAY}",
                agent_info['next_run']
            )

        console.print(table)
    else:
        console.print("[yellow]No active agents[/yellow]")

    if not status['running']:
        console.print("\n[dim]Start automation: python main.py start[/dim]")


# ========== Stats & Logs Commands ==========

@click.command(name="stats")
def stats_command():
    """Show statistics."""
    stats = db.get_stats()

    panel_content = f"""
[cyan]Total Agents:[/cyan]      {stats['total_agents']}
[cyan]Total Comments:[/cyan]    {stats['total_comments']}
[cyan]Comments Today:[/cyan]    {stats['comments_today']}
[cyan]Success Rate:[/cyan]      {stats['success_rate']}%
    """

    console.print(Panel(panel_content, title="SocialBot Statistics", border_style="cyan"))


@click.command(name="logs")
@click.option("--limit", "-n", default=20, help="Number of recent comments to show")
def logs_command(limit: int):
    """Show recent activity logs."""
    comments = db.get_recent_comments(limit=limit)

    if not comments:
        console.print("[yellow]No activity logged yet[/yellow]")
        return

    table = Table(title=f"Recent Activity (Last {limit})", box=box.ROUNDED)
    table.add_column("Time", style="dim")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Comment", style="white", max_width=50)
    table.add_column("Video", style="dim", max_width=30)

    for comment in comments:
        agent = db.get_agent(comment.agent_id)
        agent_name = agent.username if agent else f"ID:{comment.agent_id}"

        status_map = {
            "posted": "[green]✓ Posted[/green]",
            "failed": "[red]✗ Failed[/red]",
            "detected": "[yellow]⚠ Detected[/yellow]"
        }
        status = status_map.get(comment.status, comment.status)

        time_str = comment.posted_at.strftime("%m-%d %H:%M")
        comment_preview = comment.comment_text[:47] + "..." if len(comment.comment_text) > 50 else comment.comment_text
        video_preview = comment.video_url[-27:] + "..." if len(comment.video_url) > 30 else comment.video_url

        table.add_row(time_str, agent_name, status, comment_preview, video_preview)

    console.print(table)
