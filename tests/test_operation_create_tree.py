from spekulatio.operations import get_recipes
from spekulatio.operations import create_tree


def test_create_tree(fixtures_path):
    recipes = get_recipes(fixtures_path / "simple")
    root = create_tree(recipes)

    # check node types
    assert root.get("dir1").is_directory
    assert not root.get("foo.md").is_directory
    assert not root.get("dir1/baz.txt").is_directory

    # check number of nodes
    assert len(root.children.values()) == 2
    assert len(root.get("dir1").children.values()) == 1
    assert len(root.get("dir1/baz.txt").children.values()) == 0
    assert len(root.get("foo.md").children.values()) == 0
