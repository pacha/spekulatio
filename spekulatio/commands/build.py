
import sys
from pathlib import Path

import click

from spekulatio.logs import log
from spekulatio.operations import get_layers


@click.command()
@click.option(
    "-c",
    "--config",
    "config_location",
    default="./spekulatio.yaml",
    help="Configuration file to use.",
)
@click.option(
    "-v", "--verbose", default=False, is_flag=True, help="Show processing messages."
)
@click.option(
    "-vv", "--very-verbose", default=False, is_flag=True, help="Show debug information."
)
def build(
    config_location,
    verbose,
    very_verbose,
):
    """Build output directory."""

    # configure logging
    # if very_verbose:
    #     log_level = log.DEBUG
    # elif verbose:
    #     log_level = log.INFO
    # else:
    #     log_level = log.WARN

    # get layers
    try:
        spekulatio_file_path = Path(config_location)
        layers = get_layers(spekulatio_file_path)
    except Exception as err:
        log.error(f"Error reading configuration. {err}")
        sys.exit(1)

    for layer in layers:
        log.info(f"{layer.path.absolute()}")
    log.info("Done.")
