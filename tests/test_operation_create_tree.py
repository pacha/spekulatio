
from pathlib import Path

import pytest

from spekulatio.logs import log
from spekulatio.models import Layer
from spekulatio.operations import create_tree

def test_create_tree(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "simple"),
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
    assert root["dir1"].is_dir
    assert not root["foo.md"].is_dir
    assert not root["dir1"]["baz.txt"].is_dir

    # check number of nodes
    assert len(root.children) == 2
    assert len(root["dir1"].children) == 1
    assert len(root["dir1"]["baz.txt"].children) == 0
    assert len(root["foo.md"].children) == 0
