
import pytest

from spekulatio.operations import get_layers
from spekulatio.exceptions import SpekulatioInputError

def test_fail_wrong_path(fixtures_path):
    with pytest.raises(SpekulatioInputError):
        _ = get_layers(fixtures_path / "wrong-layer-path")
