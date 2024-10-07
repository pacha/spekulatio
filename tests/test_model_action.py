
from pathlib import Path

import pytest

from spekulatio.models import Action
from spekulatio.exceptions import SpekulatioValidationError

def test_action_create():
    action = Action.from_dict({
        "patterns": ["*.jpeg", "*.jpg"],
        "parameters": {
            "foo": 1,
            "bar": 2,
        }
    })
    assert action.patterns == ["*.jpeg", "*.jpg"]
    assert action.output_name_template == "{{ _this.input_path.name }}"
    assert action.parameters == {"foo": 1, "bar": 2}

def test_action_create_fail():
    with pytest.raises(SpekulatioValidationError):
        _ = Action.from_dict({
            "patterns": ["*.txt"],
            "foo": "bar",
        })

def test_action_match():
    action = Action.from_dict({
        "patterns": ["*.txt", "foo/*/bar.md"],
    })
    assert action.match("this.txt")
    assert action.match("that/this.txt")
    assert action.match("foo/baz/bar.md")
    assert not action.match("baz/foo/bar.md")
    assert not action.match("image.png")

def test_action_output_name():
    action = Action.from_dict({
        "patterns": ["*.md"],
        "output_name_template": "{{ path.with_suffix('.html').name }}",
    })
    values = {
        "path": Path("foo/baz/bar.md"),
    }
    assert action.get_output_name(values) == "bar.html"
