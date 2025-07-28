from pathlib import Path

import pytest

from spekulatio.models import Action
from spekulatio.exceptions import SpekulatioInputError


def test_action_create():
    action = Action.from_dict(
        {
            "name": "Copy",
            "patterns": ["*.jpeg", "*.jpg"],
        }
    )
    assert action.patterns == ["*.jpeg", "*.jpg"]
    assert action.output_name == "{{ _input_path.name }}"


def test_action_fail_extra_fields():
    with pytest.raises(SpekulatioInputError):
        _ = Action.from_dict(
            {
                "name": "Copy",
                "patterns": ["*.txt"],
                "foo": "bar",
            }
        )


def test_action_fail_wrong_parameters():
    with pytest.raises(SpekulatioInputError):
        _ = Action.from_dict(
            {
                "name": "Copy",
                "patterns": ["*.jpeg", "*.jpg"],
                "parameters": {
                    "foo": 1,
                    "bar": 2,
                },
            }
        )


def test_action_match():
    action = Action.from_dict(
        {
            "name": "Render",
            "patterns": ["*.txt", "foo/*/bar.md"],
        }
    )
    assert action.match(Path("/some-root"), Path("this.txt"))
    assert action.match(Path("/some-root"), Path("that/this.txt"))
    assert action.match(Path("/some-root"), Path("foo/baz/bar.md"))
    assert not action.match(Path("/some-root"), Path("baz/foo/bar.md"))
    assert not action.match(Path("/some-root"), Path("image.png"))


def test_action_output_name():
    action = Action.from_dict(
        {
            "name": "Md2Html",
            "patterns": ["*.md"],
            "output_name": "{{ _input_path.with_suffix('.html').name }}",
        }
    )
    values = {
        "_input_path": Path("bar.md"),
    }
    assert action.get_output_name(values) == "bar.html"
