
from pathlib import Path

import pytest

from spekulatio.models import Action
from spekulatio.exceptions import SpekulatioValidationError

def test_action_create():
    action = Action.from_dict({
        "name": "Copy",
        "patterns": ["*.jpeg", "*.jpg"],
    })
    assert action.patterns == ["*.jpeg", "*.jpg"]
    assert action.output_name == "{{ _input_name }}"

def test_action_fail_extra_fields():
    with pytest.raises(SpekulatioValidationError):
        _ = Action.from_dict({
            "name": "Copy",
            "patterns": ["*.txt"],
            "foo": "bar",
        })

def test_action_fail_wrong_parameters():
    with pytest.raises(SpekulatioValidationError):
        _ = Action.from_dict({
            "name": "Copy",
            "patterns": ["*.jpeg", "*.jpg"],
            "parameters": {
                "foo": 1,
                "bar": 2,
            }
        })

def test_action_match():
    action = Action.from_dict({
        "name": "Render",
        "patterns": ["*.txt", "foo/*/bar.md"],
    })
    assert action.match("this.txt")
    assert action.match("that/this.txt")
    assert action.match("foo/baz/bar.md")
    assert not action.match("baz/foo/bar.md")
    assert not action.match("image.png")

def test_action_output_name():
    action = Action.from_dict({
        "name": "Md2Html",
        "patterns": ["*.md"],
        "output_name": "{{ _input_name.with_suffix('.html') }}",
    })
    values = {
        "_input_name": Path("bar.md"),
    }
    assert action.get_output_name(values) == "bar.html"
