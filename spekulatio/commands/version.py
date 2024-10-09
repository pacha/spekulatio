import click

from spekulatio import __version__


@click.command(name="version")
def spekulatio_version():
    """Display Spekulatio version."""
    print(f"Spekulatio {__version__}")
