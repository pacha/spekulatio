
import click

from .build import build


@click.group(context_settings={"show_default": True})
def spekulatio():
    pass


spekulatio.add_command(build)  # type: ignore
