
import pytest

from spekulatio.models import Node
from spekulatio.models import Layer
from spekulatio.exceptions import SpekulatioValidationError

def test_prune(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "prune"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    # the empty dictionaries are part of the tree
    assert len(root.children) == 1
    assert len(root["dir1"].children) == 2
    assert len(root["dir1"]["dir2"].children) == 1
    assert len(root["dir1"]["dir2"]["dir3"].children) == 0
    assert len(root["dir1"]["dir4"].children) == 2
    assert len(root["dir1"]["dir4"]["dir5"].children) == 0
    assert len(root["dir1"]["dir4"]["dir6"]["some-file.md"].children) == 0

    root.prune()

    # after pruning the empty dictionaries are gone
    assert len(root.children) == 1
    assert len(root["dir1"].children) == 1
    assert "dir2" not in root["dir1"]._children
    assert len(root["dir1"]["dir4"].children) == 1
    assert "dir5" not in root["dir1"]["dir4"]._children
    assert len(root["dir1"]["dir4"]["dir6"]["some-file.md"].children) == 0


def test_prune_all(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "prune-all"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    # the empty dictionaries are part of the tree
    assert len(root.children) == 3
    assert len(root["dir1"].children) == 1
    assert len(root["dir1"]["dir5"].children) == 1
    assert len(root["dir1"]["dir5"]["dir6"].children) == 0
    assert len(root["dir2"].children) == 1
    assert len(root["dir2"]["dir4"].children) == 0
    assert len(root["dir3"].children) == 0

    root.prune()

    # after pruning the empty dictionaries are gone
    assert len(root.children) == 0
