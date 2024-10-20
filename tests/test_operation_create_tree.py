
from spekulatio.operations import get_layers
from spekulatio.operations import create_tree

def test_create_tree(fixtures_path):
    layers = get_layers(fixtures_path / "simple")
    root = create_tree(layers)

    # check node types
    assert root.get("dir1").is_dir
    assert not root.get("foo.md").is_dir
    assert not root.get("dir1/baz.txt").is_dir

    # check number of nodes
    assert len(root.children) == 2
    assert len(root.get("dir1").children) == 1
    assert len(root.get("dir1/baz.txt").children) == 0
    assert len(root.get("foo.md").children) == 0
