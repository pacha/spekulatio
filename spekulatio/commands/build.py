
import logging
from pathlib import Path

import click

from spekulatio.logs import log
from spekulatio.logs import configure_logging
from spekulatio.operations import build as build_operation


@click.command()
@click.option(
    "-s",
    "spekulatio_file",
    default="./spekulatio.yaml",
    help="Spekulatio file to read.",
)
@click.option(
    "-o",
    "--output",
    "output_location",
    required=True,
    help="Output directory.",
)
@click.option(
    "-V",
    "--values-file",
    "values_file",
    required=False,
    default="_values.yaml",
    help="Name of the values file to read in each directory.",
)
@click.option(
    "-E",
    "--extra-values-file",
    "extra_values_file",
    required=False,
    default=None,
    help="Name of the extra values file to read in each directory.",
)
@click.option(
    "-c",
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
    spekulatio_file,
    output_location,
    values_file,
    extra_values_file,
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
    spekulatio_file_path = Path(spekulatio_file)
    output_path = Path(output_location)
    build_operation(spekulatio_file_path, output_path, values_file, extra_values_file, cache=cache)
    log.debug("Done.")
