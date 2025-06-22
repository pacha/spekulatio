import pytest

from spekulatio.operations import get_recipes
from spekulatio.models import Node


def test_prune(fixtures_path):
    recipe = get_recipes(fixtures_path / "prune")[0]
    root = Node(parent=None, name=".")
    recipe.apply_to(root)

    # the empty dictionaries are part of the tree
    assert len(list(root.children.values())) == 1
    assert len(list(root.get("dir1").children.values())) == 2
    assert len(list(root.get("dir1/dir2").children.values())) == 1
    assert len(list(root.get("dir1/dir2/dir3").children.values())) == 0
    assert len(list(root.get("dir1/dir4").children.values())) == 2
    assert len(list(root.get("dir1/dir4/dir5").children.values())) == 0
    assert len(list(root.get("dir1/dir4/dir6/some-file.md").children.values())) == 0

    root.prune()

    # after pruning the empty dictionaries are gone
    assert len(list(root.children.values())) == 1
    assert len(list(root.get("dir1").children.values())) == 1
    assert "dir2" not in list(root.get("dir1").children.values())
    assert len(list(root.get("dir1/dir4").children.values())) == 1
    assert "dir5" not in list(root.get("dir1/dir4").children.values())
    assert len(list(root.get("dir1/dir4/dir6/some-file.md").children.values())) == 0


def test_prune_all(fixtures_path):
    recipe = get_recipes(fixtures_path / "prune-all")[0]
    root = Node(parent=None, name=".")
    recipe.apply_to(root)

    # the empty dictionaries are part of the tree
    assert len(list(root.children.values())) == 3
    assert len(list(root.get("dir1").children.values())) == 1
    assert len(list(root.get("dir1/dir5").children.values())) == 1
    assert len(list(root.get("dir1/dir5/dir6").children.values())) == 0
    assert len(list(root.get("dir2").children.values())) == 1
    assert len(list(root.get("dir2/dir4").children.values())) == 0
    assert len(list(root.get("dir3").children.values())) == 0

    root.prune()

    # after pruning the empty dictionaries are gone
    assert len(list(root.children.values())) == 0
