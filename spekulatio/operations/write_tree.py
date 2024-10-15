
from pathlib import Path

from spekulatio.models import Node

def write_tree(output_path: Path, root: Node) -> None:
    """Generate the output file structure from an in-memory tree."""
    for node in root.traverse():
        node.write(base_path=output_path)
