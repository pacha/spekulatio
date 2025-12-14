import sys
import logging
from pathlib import Path

import click

from spekulatio.paths import search_recipe_paths
from spekulatio.paths import DEFAULT_VALUES_FILENAME
from spekulatio.logs import log
from spekulatio.logs import configure_logging
from spekulatio.operations import build as build_operation
from spekulatio.exceptions import SpekulatioError
from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.lib.parse_values import parse_values_from_file
from spekulatio.lib.parse_values import parse_values_from_string


@click.command()
@click.argument('recipe_location')
@click.option(
    "-i",
    "--input-dir",
    "input_dir",
    required=False,
    help="Input directory.",
)
@click.option(
    "-o",
    "--output-dir",
    "output_dir",
    required=True,
    help="Output directory.",
)
@click.option(
    "-v",
    "--values",
    "value_strings",
    multiple=True,
    required=False,
    help="Values (as JSON or YAML string)",
)
@click.option(
    "-f",
    "--values-file",
    "value_files",
    multiple=True,
    required=False,
    help="Values (as path to a JSON or YAML file)",
)
@click.option(
    "-F",
    "--values-filename",
    "values_filename",
    required=False,
    default=DEFAULT_VALUES_FILENAME,
    help=f"Name of the values file to read in each directory (default: {DEFAULT_VALUES_FILENAME}).",
)
@click.option(
    "-C",
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
    "-L",
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
    default="warning",
    help="Set the logging level (debug, info, warning, error, critical)"
)
def build(
    recipe_location,
    input_dir,
    output_dir,
    value_strings,
    value_files,
    values_filename,
    cache,
    log_level,
):
    """Build output directory."""

    # logging
    upper_log_level = log_level.upper()
    numeric_log_level = getattr(logging, upper_log_level)
    configure_logging(numeric_log_level)
    log.info(f"Log level: {upper_log_level}")

    # gather values passed through command line
    value_overrides = []
    for value_file in value_files:
        value_file_path = Path(value_file)
        try:
            values_from_file = parse_values_from_file(
                value_file_path.parent,
                value_file_path.name,
                fail_if_missing=True,
            )
        except Exception as err:
            log.error(f"Impossible to read values from {value_file}. Error: {err}")
            sys.exit(1)
        log.debug(f"Values from {value_file}: {values_from_file}")
        value_overrides.append(values_from_file)

    for value_string in value_strings:
        try:
            values_from_string = parse_values_from_string(value_string)
        except Exception:
            log.error("Can't parse values in string: {value_string}")
            sys.exit(2)
        log.debug(f"Values passed as string: {values_from_string}")
        value_overrides.append(values_from_string)

    # set paths
    input_path = Path(input_dir) if input_dir else None
    output_path = Path(output_dir)
    search_paths = [Path.cwd()] + search_recipe_paths

    # build!
    build_operation(
        recipe_location,
        output_path,
        input_path,
        search_paths,
        value_overrides,
        values_filename,
        cache,
    )
    log.info("Done.")
