
from pathlib import Path

import pytest

from spekulatio.logs import log
from spekulatio.models import Node
from spekulatio.models import Layer
from spekulatio.operations import create_tree

def test_default_values(fixtures_path):
    layer = Layer.from_dict({
        "path": str(fixtures_path / "values-default"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = create_tree([layer])

    # dir1 must show the default values
    assert root["dir1"].values["_template"] == "spekulatio/default.html"
    assert root["dir1"].values["_sort"] == ["*"]

    # dir2 must show the overriden values
    assert root["dir1"]["dir2"].values["_template"] == "some-template.html"
    assert root["dir1"]["dir2"].values["_sort"] == ["foo.md", "*", "bar.md"]

    # dir2/foo.md must show the overriden value only for _template
    assert root["dir1"]["dir2"]["foo.md"].values["_template"] == "some-template.html"
    assert root["dir1"]["dir2"]["foo.md"].values["_sort"] == ["*"]

    # dir3 must show the default values
    assert root["dir1"]["dir3"].values["_template"] == "spekulatio/default.html"
    assert root["dir1"]["dir3"].values["_sort"] == ["*"]

    # dir3/foo.md must show the default values
    assert root["dir1"]["dir3"]["foo.md"].values["_template"] == "spekulatio/default.html"
    assert root["dir1"]["dir3"]["foo.md"].values["_sort"] == ["*"]

def test_values_frontmatter(fixtures_path):
    path = fixtures_path / "values-frontmatter"
    layer = Layer.from_dict({
        "path": str(path),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = create_tree([layer])
    node = root["foo.md"]
    assert node.user_values == {"foo": 1, "bar": 2}

def test_values_directory(fixtures_path):
    path = fixtures_path / "values-directory"
    layer = Layer.from_dict({
        "path": str(path),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
    })
    root = create_tree([layer])
    node = root["foo"]
    assert node.user_values == {"foo": 1, "bar": 2}

def test_values_inheritance(fixtures_path):
    layer1 = Layer.from_dict({
        "path": str(fixtures_path / "values-inheritance" / "layer1"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
        "values": {
            "e": [5],
            "f": 7,
        },
    })
    layer2 = Layer.from_dict({
        "path": str(fixtures_path / "values-inheritance" / "layer2"),
        "actions": [
            {
                "name": "Md2Html",
            },
        ],
        "values": {
            "e {insert}": 6,
            "g": 8,
        },
    })
    root = create_tree([layer1, layer2])

    # values in the layer definitions can be patched
    assert root.values["e"] == [5, 6]

    # values in a _values.yaml file are assigned to the directory that contains that file
    assert root["dir1"].values["a"] == 1

    # and they are inherited by its children
    assert root["dir1"]["dir2"].values["a"] == 1

    # unless overwritten
    assert root["dir1"]["dir2"].values["b"] == 200
    assert root["dir1"]["dir2"]["foo.md"].values["b"] == 2000

    # they can also be overwritten in another layer
    assert root["dir1"].values["c"] == 300

    # values overwritten in another layer are still inherited by children
    assert root["dir1"]["dir2"]["foo.md"].values["c"] == 300

    # values defined in the layer are inherited by all children
    assert root["dir1"].values["f"] == 7
    assert root["dir4"].values["f"] == 7
    assert root["dir1"].values["g"] == 8
    assert root["dir4"].values["g"] == 8

