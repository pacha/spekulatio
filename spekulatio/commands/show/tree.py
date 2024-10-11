
from pathlib import Path

import click
from rich import print
from rich.tree import Tree

from spekulatio.operations import get_layers
from spekulatio.operations import create_tree


@click.command(name="tree")
@click.option(
    "-c",
    "--config",
    "config_location",
    default="./spekulatio.yaml",
    help="Configuration file to use.",
)
def show_tree(config_location):
    """Show output tree."""

    def build_visualization_tree(viz_node, data_node):
        for data_child in data_node.children:
            viz_child = viz_node.add(data_child.name)
            build_visualization_tree(viz_child, data_child)

    # get output tree
    spekulatio_file_path = Path(config_location)
    layers = get_layers(spekulatio_file_path)
    data_tree = create_tree(layers)

    # create visualization tree
    viz_tree = Tree("/")
    build_visualization_tree(viz_tree, data_tree)

    # display
    print(viz_tree)
