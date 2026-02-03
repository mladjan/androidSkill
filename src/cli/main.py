"""Main CLI entry point for SocialBot."""

import click
from rich.console import Console

from src.cli.commands import agent_group, config_group, start_command, stop_command, status_command, stats_command, logs_command
from src.logger import log

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="SocialBot")
def cli():
    """
    SocialBot - TikTok Comment Automation MVP

    Manage TikTok agents, automate commenting, and monitor activity.
    """
    pass


# Register command groups
cli.add_command(agent_group)
cli.add_command(config_group)
cli.add_command(start_command)
cli.add_command(stop_command)
cli.add_command(status_command)
cli.add_command(stats_command)
cli.add_command(logs_command)


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        log.exception("Unhandled exception in CLI")
        raise


if __name__ == "__main__":
    main()
