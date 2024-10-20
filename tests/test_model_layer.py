
import pytest

from spekulatio.operations import get_layers
from spekulatio.exceptions import SpekulatioValidationError

def test_create_empty_layer(fixtures_path):
    layer = get_layers(fixtures_path / "layer-empty")[0]
    assert len(layer.actions) == 0
    assert layer.values == {}

def test_create_layer(fixtures_path):
    layer = get_layers(fixtures_path / "layer-minimal")[0]
    assert len(layer.actions[0].parser.patterns) == 2
    assert layer.values["foo"] == 1
    assert layer.values["bar"] == 2

def test_fail_create_layer(fixtures_path):
    with pytest.raises(SpekulatioValidationError):
        _ = get_layers(fixtures_path / "layer-wrong")
