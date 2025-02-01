import logging
from pathlib import Path

import click
from cels import patch_dictionary

from spekulatio.logs import log
from spekulatio.logs import configure_logging
from spekulatio.operations import build as build_operation
from spekulatio.lib.parse_values import parse_values_from_file
from spekulatio.lib.parse_values import parse_values_from_string


@click.command()
@click.argument('spekulatio_file')
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
    "values_str",
    required=False,
    help="Values (as JSON or YAML string)",
)
@click.option(
    "-f",
    "--values-file",
    "values_file",
    required=False,
    help="Values (as path to a JSON or YAML file)",
)
@click.option(
    "-D",
    "--default-values-filename",
    "default_values_filename",
    required=False,
    default="_values.yaml",
    help="Name of the values file to read in each directory.",
)
@click.option(
    "-O",
    "--override-values-filename",
    "override_values_filename",
    required=False,
    default=None,
    help="Name of the override values file to read in each directory.",
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
    "--clear-output-first",
    "clear_output_first",
    is_flag=True,
    default=False,
    help=(
        "Delete the contents of the output directory before generating the output."
    ),
)
@click.option(
    "--verbose", default=False, is_flag=True, help="Show processing messages."
)
@click.option(
    "--very-verbose", default=False, is_flag=True, help="Show debug information."
)
def build(
    spekulatio_file,
    input_dir,
    output_dir,
    values_str,
    values_file,
    default_values_filename,
    override_values_filename,
    cache,
    clear_output_first,
    verbose,
    very_verbose,
):
    """Build output directory."""

    # logging
    if very_verbose:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    configure_logging(log_level)
    log.debug(f"Log level: {logging.getLevelName(log_level)}")

    # values
    values = {}
    if values_file:
        values_file_path = Path(values_file)
        try:
            values_from_file = parse_values_from_file(
                values_file_path.parent,
                values_file_path.name,
                fail_if_missing=True,
            )
            values = patch_dictionary(values, values_from_file)
        except Exception:
            log.error("Impossible to parse values provided with the '-f/--value-file' option.")
            raise
        log.debug(f"Values passed as file: {values_from_file}")

    if values_str:
        try:
            values_from_string = parse_values_from_string(values_str)
            values = patch_dictionary(values, values_from_string)
        except Exception:
            log.error("Invalid '-v/--values' option.")
            raise
        log.debug(f"Values passed as string: {values_from_string}")
    log.debug(f"Initial values: {values}")

    # set paths
    spekulatio_file_path = Path(spekulatio_file)
    input_path = Path(input_dir) if input_dir else None
    output_path = Path(output_dir)

    # clear output directory if necessary
    if clear_output_first:
        log.debug(f"Deleting contents from {output_path}...")
        delete_directory_contents(output_path)

    return

    # build!
    log.debug("Building...")
    build_operation(
        spekulatio_file_path, output_path, values_file, extra_values_file, cache=cache
    )
    log.debug("Done.")
