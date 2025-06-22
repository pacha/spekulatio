
from pathlib import Path
from typing import Optional
from collections import defaultdict

import yaml
from schema import And
from schema import Schema
from schema import Regex
from schema import Optional as OptionalField

from spekulatio.paths import search_recipe_paths
from spekulatio.lib.paths import search_project_in_path_list
from spekulatio.paths import DEFAULT_VALUES_FILENAME
from spekulatio.paths import DEFAULT_SPEKULATIO_FILENAME
from spekulatio.models import Recipe
from spekulatio.exceptions import SpekulatioInputError

def get_recipes(
    recipe_path: Path,
    input_path: Optional[Path] = None,
    search_paths: Optional[list[Path]] = None,
    value_overrides: Optional[list[dict]] = None,
    values_filename: str = DEFAULT_VALUES_FILENAME,
) -> list[Recipe]:
    """Create the Recipe pointed to by `recipe_path` and all its children recipes.

    The recipes are returned in the order in which they should be applied to get
    the final result. The root recipe is returned as the last element of the list.
    """

    # default values for containers
    if not search_paths:
        search_paths = []
    if not value_overrides:
        value_overrides = []

    return _get_recipes_rec(
        recipe_path, input_path, search_paths, value_overrides, values_filename, values_prefix="", all_recipe_paths=set()
    )


def _get_recipes_rec(
    recipe_path: Path,
    input_path: Optional[Path],
    search_paths: list[Path],
    value_overrides: list[dict],
    values_filename: str,
    values_prefix: str,
    all_recipe_paths: set[Path],
) -> list[Recipe]:
    """Recursive version of `get_recipes`."""

    # the final list of recipes to be returned
    recipes = []

    # split overrides across recipe prefixes
    value_overrides_per_prefix = _get_overrides_per_prefix(value_overrides)

    # get actual recipe path (and include it in the list of processed ones)
    try:
        actual_recipe_path = search_project_in_path_list(
            DEFAULT_SPEKULATIO_FILENAME, recipe_path, search_paths
        )
    except ValueError as err:
        raise SpekulatioInputError(err)

    if actual_recipe_path in all_recipe_paths:
        raise SpekulatioInputError(
            f"Detected a cyclic dependency. "
            f"{recipe_path} has been already been processed."
        )
    all_recipe_paths.add(actual_recipe_path)

    # read recipe file
    try:
        text = actual_recipe_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
    except Exception as err:
        raise SpekulatioInputError(
            f"Can't read configuration file '{actual_recipe_path}'. Reason: {err}."
        )

    # get linked layer definitions
    raw_layer_definitions = data.pop("layers", [])
    layer_definitions = _validate_layer_definitions(raw_layer_definitions)
    for layer_definition in layer_definitions:
        prefix = layer_definition.get("id")
        layer_input_path = layer_definition.get("input_path", input_path)
        recipes.extend(
            _get_recipes_rec(
                recipe_path=Path(layer_definition["path"]),
                input_path=Path(layer_input_path) if layer_input_path else None,
                search_paths=[actual_recipe_path.parent] + search_recipe_paths,
                value_overrides=[layer_definition.get("values", {})] + value_overrides_per_prefix[prefix],
                values_filename=layer_definition.get("values_filename", DEFAULT_VALUES_FILENAME),
                values_prefix=f"{values_prefix}.{prefix}",
                all_recipe_paths=all_recipe_paths,
            )
        )

    # add current recipe
    if data:
        try:
            recipe = Recipe.from_dict(
                data=data,
                current_path=actual_recipe_path.parent,
                input_path=input_path,
                value_overrides=value_overrides_per_prefix[""],
                values_filename=values_filename,
                recipe_filename=actual_recipe_path.name,
            )
        except Exception as err:
            raise
            raise SpekulatioInputError(f"Error found while processing '{actual_recipe_path}': {err}")
        recipes.append(recipe)


    return recipes

def _validate_layer_definitions(raw_layer_definitions: list[dict]) -> list[dict]:
    """Check that the layer definitions in the recipe match expectations about them."""

    if not isinstance(raw_layer_definitions, list):
        raise SpekulatioInputError(
            f"{spekulatio_file_path}: 'layers' should be a list of dictionaries."
        )

    schema = Schema(
        {
            OptionalField("id"): And(
                str, Regex(r'^[A-Za-z_]+$'), error="If provided, 'id' must be a string of uppercase and lowercase letters, plus underscores."
            ),
            "path": And(
                str, len, error="'path' in 'layers' should be a non-empty string."
            ),
            OptionalField("input_path"): And(
                str, len, error="'input_path' in 'layers' should be a non-empty string."
            ),
            OptionalField("values"): {str: object},
            OptionalField("values_filename"): And(
                str, len, error="If provided, 'values_filename' should be a non-empty string."
            ),
        }
    )

    layer_definitions = []
    for layer_definition in raw_layer_definitions:
        layer_definitions.append(schema.validate(layer_definition))
    return layer_definitions

def _get_overrides_per_prefix(value_overrides: list[dict]) -> defaultdict[str, list[dict]]:
    """Split a list of values overrides according to their intended recipe."""

    value_overrides_per_prefix = defaultdict(list)

    for value_override_dict in value_overrides:
        for key, value in _split_value_overrides(value_override_dict).items():
            value_overrides_per_prefix[key].append(value)
    return value_overrides_per_prefix

def _split_value_overrides(value_overrides: dict) -> defaultdict:
    """Split values according to their intended recipe."""

    split_value_overrides = defaultdict(dict)

    for key, value in value_overrides.items():
        parts = key.split('.')
        if len(parts) == 1:
            split_value_overrides[""][key] = value
        else:
            prefix = parts[0]
            key_without_prefix = key[len(prefix) + 1:]
            split_value_overrides[prefix][key_without_prefix] = value

    return split_value_overrides

