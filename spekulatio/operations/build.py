
import logging

from pathlib import Path

from spekulatio.logs import log

from .get_layers import get_layers
from .create_tree import create_tree
from .write_tree import write_tree

def build(spekulatio_file_path: Path, output_path: Path) -> None:
    """Build project from a spekulation configuration file."""

    log.debug("Reading layer configuration...")
    layers = get_layers(spekulatio_file_path)

    log.debug("Creating in-memory tree...")
    root = create_tree(layers)

    log.debug("Writing output...")
    write_tree(output_path, root)
