
from pathlib import Path

import click
from rich import print

from spekulatio.operations import get_layers


@click.command(name="layers")
@click.option(
    "-c",
    "--config",
    "config_location",
    default="./spekulatio.yaml",
    help="Configuration file to use.",
)
def show_layers(config_location):
    """Show layers defined in spekulatio.yaml."""

    # get layers
    spekulatio_file_path = Path(config_location)
    layers = get_layers(spekulatio_file_path)

    for index, layer in enumerate(layers):
        print(f"Layer {index}:")
        print(f"  path: {layer.path}")
        print(f"  mount at: {layer.mount_at}")
