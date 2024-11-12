
import logging
from pathlib import Path

import click

from spekulatio.logs import log
from spekulatio.logs import configure_logging
from spekulatio.operations import build as build_operation


@click.command()
@click.option(
    "-c",
    "--config",
    "config_location",
    default="./spekulatio.yaml",
    help="Configuration file to use.",
)
@click.option(
    "-o",
    "--output",
    "output_location",
    required=True,
    help="Output directory.",
)
@click.option(
    "-o",
    "--output",
    "output_location",
    required=True,
    help="Output directory.",
)
@click.option(
    "--cache",
    "cache",
    is_flag=True,
    default=False,
    help=(
        "Don't generate output files if they exist and have a newer update timestamp "
        "than the associated input ones."
    ),
)
@click.option(
    "-v", "--verbose", default=False, is_flag=True, help="Show processing messages."
)
@click.option(
    "-vv", "--very-verbose", default=False, is_flag=True, help="Show debug information."
)
def build(
    config_location,
    output_location,
    cache,
    verbose,
    very_verbose,
):
    """Build output directory."""

    # configure logging
    if very_verbose:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    configure_logging(log_level)
    log.debug(f"Log level: {logging.getLevelName(log_level)}")

    log.debug("Building...")
    config_path = Path(config_location)
    output_path = Path(output_location)
    build_operation(config_path, output_path, cache=cache)
    log.debug("Done.")
