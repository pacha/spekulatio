
from spekulatio.models import Node
from spekulatio.models import Layer

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

def test_sorting(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "sorting"),
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
