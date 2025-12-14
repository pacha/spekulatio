from pathlib import Path
from typing import Optional

from spekulatio.logs import log
from spekulatio.paths import DEFAULT_VALUES_FILENAME

from .get_recipes import get_recipes
from .create_tree import create_tree
from .write_tree import write_tree


def build(
    recipe_location: str,
    output_path: Path,
    input_path: Optional[Path] = None,
    search_paths: Optional[list[Path]] = None,
    value_overrides: Optional[list[dict]] = None,
    values_filename: str = DEFAULT_VALUES_FILENAME,
    cache: bool = False,
) -> None:
    """Build recipe."""

    # default values for containers
    if not search_paths:
        search_paths = []
    if not value_overrides:
        value_overrides = []

    log.info("Reading recipes...")
    recipes = get_recipes(recipe_location, input_path, search_paths, value_overrides, values_filename)
    if not recipes:
        log.warning("Empty recipe. No output will be generated.")

    log.info("Creating in-memory tree...")
    root = create_tree(recipes)

    log.info("Writing output...")
    write_tree(output_path, root, cache=cache)
