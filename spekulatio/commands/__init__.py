import sys
import logging

import click

from .show import show
from .build import build
from .serve import serve
from .version import version

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioError
from spekulatio.exceptions import SpekulatioInternalError


class CustomGroup(click.Group):
    def invoke(self, ctx):
        try:
            super().invoke(ctx)
        except SpekulatioError as err:
            log.error(err)
            sys.exit(3)
        except (SpekulatioInternalError, Exception) as err:
            log.exception(f"An unexpected error occurred: {err}.\n\nFull traceback shown:\n\n")
            sys.exit(4)

@click.group(cls=CustomGroup, context_settings={"show_default": True})
def spekulatio():
    pass


spekulatio.add_command(show)  # type: ignore
spekulatio.add_command(build)  # type: ignore
spekulatio.add_command(serve)  # type: ignore
spekulatio.add_command(version)  # type: ignore
