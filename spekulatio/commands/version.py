import click

from spekulatio import __version__


@click.command
def version():
    """Display Spekulatio version."""
    print(f"Spekulatio {__version__}")
