
from spekulatio.operations import get_layers
from spekulatio.operations import create_tree

def test_default_values(fixtures_path):
    layers = get_layers(fixtures_path / "values-default")
    root = create_tree(layers)

    # dir1 must show the default values
    assert root.get("dir1").values["_template"] == "spekulatio/default.html"
    assert root.get("dir1").values["_sort"] == ["*"]

    # dir2 must show the overriden values
    assert root.get("dir1/dir2").values["_template"] == "some-template.html"
    assert root.get("dir1/dir2").values["_sort"] == ["foo.md", "*", "bar.md"]

    # dir2/foo.md must show the overriden value only for _template
    assert root.get("dir1/dir2/foo.md").values["_template"] == "some-template.html"
    assert root.get("dir1/dir2/foo.md").values["_sort"] == ["*"]

    # dir3 must show the default values
    assert root.get("dir1/dir3").values["_template"] == "spekulatio/default.html"
    assert root.get("dir1/dir3").values["_sort"] == ["*"]

    # dir3/foo.md must show the default values
    assert root.get("dir1/dir3/foo.md").values["_template"] == "spekulatio/default.html"
    assert root.get("dir1/dir3/foo.md").values["_sort"] == ["*"]

def test_values_frontmatter(fixtures_path):
    layers = get_layers(fixtures_path / "values-frontmatter")
    root = create_tree(layers)

    node = root / "foo.md"
    assert node.user_values == {"foo": 1, "bar": 2}

def test_values_directory(fixtures_path):
    layers = get_layers(fixtures_path / "values-directory")
    root = create_tree(layers)

    node = root / "foo"
    assert node.user_values == {"foo": 1, "bar": 2}

def test_values_inheritance(fixtures_path):
    layers = get_layers(fixtures_path / "values-inheritance")
    root = create_tree(layers)

    # values in the layer definitions can be patched
    assert root.values["e"] == [5, 6]

    # values in a _values.yaml file are assigned to the directory that contains that file
    assert root.get("dir1").values["a"] == 1

    # and they are inherited by its children
    assert root.get("dir1/dir2").values["a"] == 1

    # unless overwritten
    assert root.get("dir1/dir2").values["b"] == 200
    assert root.get("dir1/dir2/foo.md").values["b"] == 2000

    # they can also be overwritten in another layer
    assert root.get("dir1").values["c"] == 300

    # values overwritten in another layer are still inherited by children
    assert root.get("dir1/dir2/foo.md").values["c"] == 300

    # values defined in the layer are inherited by all children
    assert root.get("dir1").values["f"] == 7
    assert root.get("dir4").values["f"] == 7
    assert root.get("dir1").values["g"] == 8
    assert root.get("dir4").values["g"] == 8

