import pytest

from spekulatio.operations import get_recipes
from spekulatio.exceptions import SpekulatioValidationError


def test_create_empty_recipe(fixtures_path):
    recipe = get_recipes(fixtures_path / "recipe-empty")[0]
    assert len(recipe.actions) == 0
    assert recipe.values == {}


def test_create_recipe(fixtures_path):
    recipe = get_recipes(fixtures_path / "recipe-minimal")[0]
    assert len(recipe.actions[1].parser.patterns) == 2
    assert recipe.values["foo"] == 1
    assert recipe.values["bar"] == 2


def test_fail_create_recipe(fixtures_path):
    with pytest.raises(SpekulatioValidationError):
        _ = get_recipes(fixtures_path / "recipe-wrong")
