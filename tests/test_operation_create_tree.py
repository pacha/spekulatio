
from pathlib import Path

import pytest

from spekulatio.logs import log
from spekulatio.models import Layer
from spekulatio.operations import create_tree

def test_create_tree(fixtures_path):
    path = fixtures_path / "simple"
    layer = Layer.from_dict({
        "path": str(path),
        "mount_at": "this/that",
        "actions": [
            {
                "name": "Md2Html",
            },
            {
                "name": "Render",
                "patterns": ["*.txt"],
            },
        ],
    })
    root = create_tree([layer])

    # check node types
    assert root["this"].is_dir
    assert root["this"]["that"].is_dir
    assert root["this"]["that"]["dir1"].is_dir
    assert not root["this"]["that"]["foo.md"].is_dir
    assert not root["this"]["that"]["dir1"]["baz.txt"].is_dir

    # check number of nodes
    assert len(root.children) == 1
    assert len(root["this"].children) == 1
    assert len(root["this"]["that"].children) == 2
    assert len(root["this"]["that"]["dir1"].children) == 1
    assert len(root["this"]["that"]["dir1"]["baz.txt"].children) == 0
    assert len(root["this"]["that"]["foo.md"].children) == 0
