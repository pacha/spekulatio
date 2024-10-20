
from pathlib import Path

from .get_layers import get_layers
from .create_tree import create_tree
from .write_tree import write_tree

def build(spekulatio_file_path: Path, output_path: Path) -> None:
    """Build project from a spekulation configuration file."""
    layers = get_layers(spekulatio_file_path)
    root = create_tree(layers)
    write_tree(output_path, root)
