
from pathlib import Path

import pytest

from spekulatio.logs import log
from spekulatio.models import Layer
from spekulatio.models.actions import Render
from spekulatio.models.actions import Md2Html
from spekulatio.exceptions import SpekulatioValidationError

def test_create_empty_layer(fixtures_path):
    path = fixtures_path / "minimal"
    layer = Layer.from_dict({"path": str(path)})
    assert layer.path == path
    assert len(layer.actions) == 0
    assert layer.values == {}

def test_create_layer(fixtures_path):
    path = fixtures_path / "minimal"
    layer = Layer.from_dict({
        "path": str(path),
        "actions": [
            {
                "name": "Md2Html",
                "patterns": ["*.md", "*.markdown"],
            },
        ],
        "values": {
            "foo": 1,
            "bar": 2,
        }
    })
    assert layer.path == path
    assert len(layer.actions[0].parser.patterns) == 2
    assert layer.values["foo"] == 1
    assert layer.values["bar"] == 2

def test_fail_create_layer():

    with pytest.raises(SpekulatioValidationError):
        _ = Layer.from_dict({
            "path": 100,
        })
