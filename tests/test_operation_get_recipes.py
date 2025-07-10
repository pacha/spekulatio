
from pathlib import Path

import pytest

from spekulatio.operations.get_recipes import get_recipes
from spekulatio.operations.get_recipes import _split_value_overrides
from spekulatio.operations.get_recipes import _get_overrides_per_prefix
from spekulatio.exceptions import SpekulatioInputError

def test_recipe_fail_wrong_path(fixtures_path):
    with pytest.raises(SpekulatioInputError):
        _ = get_recipes(fixtures_path / "wrong-layer-path")

def test_recipe_simple(fixtures_path):
    recipes = get_recipes(
        recipe_path=Path("recipe-simple"),
        search_paths=[fixtures_path],
        value_overrides=[{"a": 150, "e": 550, "f": 650}, {"a": 175, "b": 250, "c {delete}": None}]
    )
    assert len(recipes) == 1

    recipe = recipes[0]
    assert recipe.input_path == fixtures_path / "recipe-simple"
    assert recipe.actions == []
    assert recipe.values == {
        "a": 175,
        "b": 250,
        "d": 400,
        "e": 550,
        "f": 650,
    }
    assert recipe.values_filename == "_values.yaml"
    assert recipe.recipe_filename == "spekulatio.yaml"

def test_recipe_nested(fixtures_path):
    recipes = get_recipes(
        recipe_path=Path("recipe-nested"),
        input_path=Path("/foo"),
        search_paths=[fixtures_path],
    )
    assert len(recipes) == 2

    nested_recipe = recipes[0]
    assert nested_recipe.input_path == Path("/foo")
    assert nested_recipe.actions == []
    assert nested_recipe.values == {
        "foo": "bar",
        "baz": "that",
    }
    assert nested_recipe.values_filename == "_values.yaml"
    assert nested_recipe.recipe_filename == "spekulatio.yaml"

    root_recipe = recipes[1]
    assert root_recipe.input_path == fixtures_path / "recipe-nested"
    assert root_recipe.actions == []
    assert root_recipe.values == {
        "a": 100,
    }
    assert root_recipe.values_filename == "_values.yaml"
    assert root_recipe.recipe_filename == "spekulatio.yaml"

def test_recipe_actions(fixtures_path):
    recipes = get_recipes(
        recipe_path=Path("recipe-actions"),
        search_paths=[fixtures_path],
    )
    assert len(recipes) == 1

    recipe = recipes[0]
    assert recipe.input_path == fixtures_path / "recipe-actions"
    assert set([action.name() for action in recipe.actions]) == {"Md2Html"}

def test_split_value_overrides():
    """Test splitting user provided values across recipes."""

    value_overrides = {
        "prefix1.key1": 100,
        "prefix1.prefix2.key2": 200,
        "prefix1.prefix2.prefix3.prefix4.key3": 300,
        "prefix5.key4": 400,
        "prefix5.key5": 500,
        ".key6": 600,
        "key7": 700,
    }

    expected_result = {
        "prefix1": {
            "key1": 100,
            "prefix2.key2": 200,
            "prefix2.prefix3.prefix4.key3": 300,
        },
        "prefix5": {
            "key4": 400,
            "key5": 500,
        },
        "": {
            "key6": 600,
            "key7": 700,
        },
    }

    result = _split_value_overrides(value_overrides)
    assert result == expected_result

def test_get_overrides_per_prefix():
    """Test splitting a list of overrides."""
    value_overrides = [
        {
            "prefix1.key1": 100,
            "prefix1.prefix2.key2": 200,
            "prefix5.key4": 400,
            "key7": 700,
        },
        {
            "prefix1.key1": 500,
        },
        {
            "key8": 800,
        },
    ]
    expected_result = {
        "prefix1": [
            {
                "key1": 100,
                "prefix2.key2": 200,
            },
            {
                "key1": 500,
            },
        ],
        "prefix5": [
            {
                "key4": 400,
            },
        ],
        "": [
            {
                "key7": 700,
            },
            {
                "key8": 800,
            },
        ],
    }
    result = _get_overrides_per_prefix(value_overrides)
    assert result == expected_result

