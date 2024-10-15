
import pytest

from spekulatio.models import Node
from spekulatio.models import Layer
from spekulatio.exceptions import SpekulatioValidationError

def test_sorting_default(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-default"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    # prev sibling
    assert root["dir1"]["a.md"].prev_sibling is None
    assert root["dir1"]["b.md"].prev_sibling == root["dir1"]["a.md"]
    assert root["dir1"]["c.md"].prev_sibling == root["dir1"]["b.md"]
    assert root["dir1"]["d.md"].prev_sibling == root["dir1"]["c.md"]
    assert root["dir1"]["e.md"].prev_sibling == root["dir1"]["d.md"]

    # next sibling
    assert root["dir1"]["a.md"].next_sibling == root["dir1"]["b.md"]
    assert root["dir1"]["b.md"].next_sibling == root["dir1"]["c.md"]
    assert root["dir1"]["c.md"].next_sibling == root["dir1"]["d.md"]
    assert root["dir1"]["d.md"].next_sibling == root["dir1"]["e.md"]
    assert root["dir1"]["e.md"].next_sibling is None

    # prev node
    assert root["dir1"]["a.md"].prev is root["dir1"]
    assert root["dir1"]["b.md"].prev == root["dir1"]["a.md"]
    assert root["dir1"]["c.md"].prev == root["dir1"]["b.md"]
    assert root["dir1"]["d.md"].prev == root["dir1"]["c.md"]
    assert root["dir1"]["e.md"].prev == root["dir1"]["d.md"]

    # next next
    assert root["dir1"]["a.md"].next == root["dir1"]["b.md"]
    assert root["dir1"]["b.md"].next == root["dir1"]["c.md"]
    assert root["dir1"]["c.md"].next == root["dir1"]["d.md"]
    assert root["dir1"]["d.md"].next == root["dir1"]["e.md"]
    assert root["dir1"]["e.md"].next is root["f.md"]

    # root
    assert root.prev is None
    assert root.prev_sibling is None
    assert root.next_sibling is None
    assert root.next is root["dir1"]

def test_sorting_sink(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-sink"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    # prev sibling
    assert root["dir1"]["b.md"].prev_sibling is None
    assert root["dir1"]["c.md"].prev_sibling == root["dir1"]["b.md"]
    assert root["dir1"]["d.md"].prev_sibling == root["dir1"]["c.md"]
    assert root["dir1"]["e.md"].prev_sibling == root["dir1"]["d.md"]
    assert root["dir1"]["a.md"].prev_sibling == root["dir1"]["e.md"]

    # next sibling
    assert root["dir1"]["b.md"].next_sibling == root["dir1"]["c.md"]
    assert root["dir1"]["c.md"].next_sibling == root["dir1"]["d.md"]
    assert root["dir1"]["d.md"].next_sibling == root["dir1"]["e.md"]
    assert root["dir1"]["e.md"].next_sibling == root["dir1"]["a.md"]
    assert root["dir1"]["a.md"].next_sibling is None

    # prev node
    assert root["dir1"]["b.md"].prev is root["dir1"]
    assert root["dir1"]["c.md"].prev == root["dir1"]["b.md"]
    assert root["dir1"]["d.md"].prev == root["dir1"]["c.md"]
    assert root["dir1"]["e.md"].prev == root["dir1"]["d.md"]
    assert root["dir1"]["a.md"].prev == root["dir1"]["e.md"]

    # next next
    assert root["dir1"]["b.md"].next == root["dir1"]["c.md"]
    assert root["dir1"]["c.md"].next == root["dir1"]["d.md"]
    assert root["dir1"]["d.md"].next == root["dir1"]["e.md"]
    assert root["dir1"]["e.md"].next == root["dir1"]["a.md"]
    assert root["dir1"]["a.md"].next is root["f.md"]

    # root
    assert root.prev is None
    assert root.prev_sibling is None
    assert root.next_sibling is None
    assert root.next is root["dir1"]

def test_sorting_sink_top(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-sink-top"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    assert [child.name for child in root["dir1"].children] == ["c.md", "d.md", "e.md", "b.md", "a.md"]

def test_sorting_sink_bottom(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-sink-bottom"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    assert [child.name for child in root["dir1"].children] == ["b.md", "e.md", "a.md", "c.md", "d.md"]

def test_sorting_duplicate(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-duplicate"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    with pytest.raises(SpekulatioValidationError):
        _ = root["dir1"].children

def test_sorting_duplicate_sink(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting-duplicate-sink"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = Node(name=".")
    layer.apply_to(root)

    with pytest.raises(SpekulatioValidationError):
        _ = root["dir1"].children
