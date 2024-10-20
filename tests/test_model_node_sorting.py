
import pytest

from spekulatio.operations import get_layers
from spekulatio.operations import create_tree
from spekulatio.exceptions import SpekulatioValidationError

def test_sorting_default(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-default")
    root = create_tree(layers)

    # prev sibling
    assert root.get("dir1/a.md").prev_sibling is None
    assert root.get("dir1/b.md").prev_sibling == root / "dir1" / "a.md"
    assert root.get("dir1/c.md").prev_sibling == root / "dir1" / "b.md"
    assert root.get("dir1/d.md").prev_sibling == root / "dir1" / "c.md"
    assert root.get("dir1/e.md").prev_sibling == root / "dir1" / "d.md"

    # next sibling
    assert root.get("dir1/a.md").next_sibling == root / "dir1" / "b.md"
    assert root.get("dir1/b.md").next_sibling == root / "dir1" / "c.md"
    assert root.get("dir1/c.md").next_sibling == root / "dir1" / "d.md"
    assert root.get("dir1/d.md").next_sibling == root / "dir1" / "e.md"
    assert root.get("dir1/e.md").next_sibling is None

    # prev node
    assert root.get("dir1/a.md").prev is root / "dir1"
    assert root.get("dir1/b.md").prev == root / "dir1" / "a.md"
    assert root.get("dir1/c.md").prev == root / "dir1" / "b.md"
    assert root.get("dir1/d.md").prev == root / "dir1" / "c.md"
    assert root.get("dir1/e.md").prev == root / "dir1" / "d.md"

    # next next
    assert root.get("dir1/a.md").next == root / "dir1" / "b.md"
    assert root.get("dir1/b.md").next == root / "dir1" / "c.md"
    assert root.get("dir1/c.md").next == root / "dir1" / "d.md"
    assert root.get("dir1/d.md").next == root / "dir1" / "e.md"
    assert root.get("dir1/e.md").next is root / "f.md"

    # root
    assert root.prev is None
    assert root.prev_sibling is None
    assert root.next_sibling is None
    assert root.next is root / "dir1"

def test_sorting_sink(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-sink")
    root = create_tree(layers)

    # prev sibling
    assert root.get("dir1/b.md").prev_sibling is None
    assert root.get("dir1/c.md").prev_sibling == root / "dir1" / "b.md"
    assert root.get("dir1/d.md").prev_sibling == root / "dir1" / "c.md"
    assert root.get("dir1/e.md").prev_sibling == root / "dir1" / "d.md"
    assert root.get("dir1/a.md").prev_sibling == root / "dir1" / "e.md"

    # next sibling
    assert root.get("dir1/b.md").next_sibling == root / "dir1" / "c.md"
    assert root.get("dir1/c.md").next_sibling == root / "dir1" / "d.md"
    assert root.get("dir1/d.md").next_sibling == root / "dir1" / "e.md"
    assert root.get("dir1/e.md").next_sibling == root / "dir1" / "a.md"
    assert root.get("dir1/a.md").next_sibling is None

    # prev node
    assert root.get("dir1/b.md").prev is root / "dir1"
    assert root.get("dir1/c.md").prev == root / "dir1" / "b.md"
    assert root.get("dir1/d.md").prev == root / "dir1" / "c.md"
    assert root.get("dir1/e.md").prev == root / "dir1" / "d.md"
    assert root.get("dir1/a.md").prev == root / "dir1" / "e.md"

    # next next
    assert root.get("dir1/b.md").next == root / "dir1" / "c.md"
    assert root.get("dir1/c.md").next == root / "dir1" / "d.md"
    assert root.get("dir1/d.md").next == root / "dir1" / "e.md"
    assert root.get("dir1/e.md").next == root / "dir1" / "a.md"
    assert root.get("dir1/a.md").next is root / "f.md"

    # root
    assert root.prev is None
    assert root.prev_sibling is None
    assert root.next_sibling is None
    assert root.next is root / "dir1"

def test_sorting_sink_top(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-sink-top")
    root = create_tree(layers)

    assert [child.name for child in root.get("dir1").children] == ["c.md", "d.md", "e.md", "b.md", "a.md"]

def test_sorting_sink_bottom(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-sink-bottom")
    root = create_tree(layers)

    assert [child.name for child in root.get("dir1").children] == ["b.md", "e.md", "a.md", "c.md", "d.md"]

def test_sorting_duplicate(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-duplicate")

    with pytest.raises(SpekulatioValidationError):
        _ = create_tree(layers)

def test_sorting_duplicate_sink(fixtures_path):
    layers = get_layers(fixtures_path / "sorting-duplicate-sink")

    with pytest.raises(SpekulatioValidationError):
        _ = create_tree(layers)
