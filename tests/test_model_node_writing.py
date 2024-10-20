
import pytest

from spekulatio.operations import get_layers
from spekulatio.operations import create_tree
from spekulatio.operations import write_tree

def test_writing(fixtures_path):
    """Test writing a tree to disk."""
    # layers = get_layers(fixtures_path / "website-project" / "spekulatio.yaml")
    # root = create_tree(layers)
    # write_tree(fixtures_path / "output", root)
