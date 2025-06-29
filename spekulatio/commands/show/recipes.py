from pathlib import Path

import click
from rich import print as rich_print

from spekulatio.logs import configure_logging
from spekulatio.operations import get_recipes
from spekulatio.paths import search_recipe_paths


@click.command(name="recipes")
@click.argument('recipe')
def show_recipes(recipe):
    """Show recipes in the order in which they'll be applied."""

    configure_logging()

    # get all nested recipes
    recipe_path = Path(recipe)
    search_paths = [Path.cwd()] + search_recipe_paths
    recipes = get_recipes(recipe_path, search_paths=search_paths)

    # display paths in stdout
    for recipe in recipes:
        rich_print(recipe)
