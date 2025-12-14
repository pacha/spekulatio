from pathlib import Path

import click
from rich import print as rich_print
from rich.tree import Tree

from spekulatio.operations import get_recipes
from spekulatio.operations import create_tree
from spekulatio.logs import configure_logging
from spekulatio.paths import search_recipe_paths


@click.command(name="tree")
@click.argument('recipe_location')
def show_tree(recipe_location):
    """Show output tree."""

    configure_logging()

    def build_visualization_tree(viz_node, data_node):
        for data_child in data_node.sorted_children:
            viz_child = viz_node.add(
                f"{data_child.name} → {data_child.output_name} "
                f"[magenta]{data_child.action}[/magenta]"
            )
            build_visualization_tree(viz_child, data_child)

    # get output tree
    search_paths = [Path.cwd()] + search_recipe_paths
    recipes = get_recipes(recipe_location, search_paths=search_paths)
    data_tree = create_tree(recipes)

    # create visualization tree
    viz_tree = Tree("/")
    build_visualization_tree(viz_tree, data_tree)

    # display
    rich_print(viz_tree)
