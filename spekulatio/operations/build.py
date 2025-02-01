from pathlib import Path
from typing import Optional

from spekulatio.logs import log

from .get_layers import get_layers
from .create_tree import create_tree
from .write_tree import write_tree


def build(
    spekulatio_file_path: Path,
    output_path: Path,
    values_file: str = "_values.yaml",
    extra_values_file: Optional[str] = None,
    cache: bool = False,
) -> None:
    """Build project from a spekulation configuration file."""

    log.debug("Reading layer configuration...")
    layers = get_layers(
        spekulatio_file_path,
        values_file=values_file,
        extra_values_file=extra_values_file,
    )

    log.debug("Creating in-memory tree...")
    root = create_tree(layers)

    log.debug("Writing output...")
    write_tree(output_path, root, cache=cache)
