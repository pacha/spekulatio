
import pytest

from spekulatio.operations import get_layers
from spekulatio.operations import create_tree
from spekulatio.exceptions import SpekulatioInputError

def test_traversing_with_get(fixtures_path):
    layers = get_layers(fixtures_path / "traversing")
    root = create_tree(layers)

    # test one node per string
    assert root == root.get()
    assert root == root.get("")
    assert root.get("dir1").name == "dir1"
    assert root.get("dir1", "dir2").name == "dir2"
    assert root.get("dir1", "dir2", "dir3").name == "dir3"
    assert root.get("dir1", "dir2", "dir3", "file.md").name == "file.md"

    # test full path in one string
    assert root.get("dir1/dir2").name == "dir2"
    assert root.get("dir1/dir2/dir3").name == "dir3"
    assert root.get("dir1/dir2/dir3/file.md").name == "file.md"

    # test mixed strings
    assert root.get("dir1", "dir2/dir3").name == "dir3"
    assert root.get("dir1/dir2", "dir3/file.md").name == "file.md"

    # test absolute paths
    assert root.get("/") == root
    assert root.get("/dir1/dir2").name == "dir2"

    # test from non-root node
    dir2 = root.get("/dir1/dir2")
    assert dir2.get("dir3").name == "dir3"
    assert dir2.get("dir3/file.md").name == "file.md"
    assert dir2.get("/dir1").name == "dir1"
    assert dir2.get("/dir1/dir2").name == "dir2"

def test_traversing_with_truediv(fixtures_path):
    layers = get_layers(fixtures_path / "traversing")
    root = create_tree(layers)

    # test one node per string
    assert root == root.get()
    assert root == root.get("")
    assert (root / "dir1").name == "dir1"
    assert (root / "dir1" / "dir2").name == "dir2"
    assert (root / "dir1" / "dir2" / "dir3").name == "dir3"
    assert (root / "dir1" / "dir2" / "dir3" / "file.md").name == "file.md"

    # test full path in one string
    assert (root / "dir1/dir2").name == "dir2"
    assert (root / "dir1/dir2/dir3").name == "dir3"
    assert (root / "dir1/dir2/dir3/file.md").name == "file.md"

    # test mixed strings
    assert (root / "dir1" / "dir2/dir3").name == "dir3"
    assert (root / "dir1/dir2" / "dir3/file.md").name == "file.md"

    # test absolute paths
    assert (root / "/") == root
    assert (root / "/dir1/dir2").name == "dir2"

    # test from non-root node
    dir2 = root / "dir1/dir2"
    assert dir2 == root / "/dir1/dir2"
    assert (dir2 / "dir3").name == "dir3"
    assert (dir2 / "dir3/file.md").name == "file.md"
    assert (dir2 / "/dir1").name == "dir1"
    assert (dir2 / "/dir1/dir2").name == "dir2"

def test_fail_traversing(fixtures_path):
    layers = get_layers(fixtures_path / "traversing")
    root = create_tree(layers)

    with pytest.raises(SpekulatioInputError):
        _ = root.get("dir1/dir3")
