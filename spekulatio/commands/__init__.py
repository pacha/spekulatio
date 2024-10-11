
import click

from .show import show
from .build import build
from .version import version


@click.group(context_settings={"show_default": True})
def spekulatio():
    pass


spekulatio.add_command(show)  # type: ignore
spekulatio.add_command(build)  # type: ignore
spekulatio.add_command(version)  # type: ignore
