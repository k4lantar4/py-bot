"""
Main CLI script for the MRJ Bot.
"""

import click
from bot.cli.db import db

@click.group()
def cli():
    """MRJ Bot CLI - Manage your V2Ray bot and services."""
    pass

# Add database commands
cli.add_command(db)

if __name__ == '__main__':
    cli() 