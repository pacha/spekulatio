import logging

import click

from .show import show
from .build import build
from .serve import serve
from .version import version

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from spekulatio.exceptions import SpekulatioInternalError


class CustomGroup(click.Group):
    def invoke(self, ctx):
        try:
            super().invoke(ctx)
        except SpekulatioInputError as err:
            log.error(err)
        except (Exception, SpekulatioInternalError) as err:
            log_level = logging.getLevelName(log.getEffectiveLevel())
            if log_level == "DEBUG":
                log.exception(f"An unexpected error occurred: {err}")
            else:
                log.error(f"An unexpected error occurred: {err}")


@click.group(cls=CustomGroup, context_settings={"show_default": True})
def spekulatio():
    pass


spekulatio.add_command(show)  # type: ignore
spekulatio.add_command(build)  # type: ignore
spekulatio.add_command(serve)  # type: ignore
spekulatio.add_command(version)  # type: ignore
