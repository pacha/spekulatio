import click

from .tree import show_tree
from .layers import show_layers
from .recipes import show_recipes


@click.group(context_settings={"show_default": True})
def show():
    """Display layers and nodes without building."""
    pass


show.add_command(show_tree)  # type: ignore
show.add_command(show_layers)  # type: ignore
show.add_command(show_recipes)  # type: ignore
