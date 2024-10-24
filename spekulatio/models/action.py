import importlib
from typing import Any
from pathlib import Path
from dataclasses import field
from dataclasses import dataclass

from schema import And
from schema import Schema
from schema import Optional
from jinja2 import Template
from py_walk import get_parser_from_list
from py_walk.models.parser import Parser

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.exceptions import SpekulatioValidationError
from spekulatio.lib.parse_values import parse_values_from_frontmatter


@dataclass
class Action:
    patterns: tuple[str] = field(default_factory=tuple)
    output_name: str = "{{ _input_name }}"
    parameters: dict[str, Any] = field(default_factory=dict)
    parser: Parser = field(init=False)

    def __post_init__(self):
        self.parser = get_parser_from_list(self.patterns)

    @classmethod
    @property
    def name(cls):
        return cls.__class__.__name__

    @classmethod
    def from_dict(cls, data):
        """Create an instance object from a data dictionary."""
        # validate
        try:
            schema = Schema(
                {
                    "name": And(str, error="'name' should be a string."),
                    Optional("package", default="spekulatio"): And(str, error="'package' should be a string."),
                    Optional("patterns"): And([str], error="'patterns' should be a list of strings."),
                    Optional("output_name"): And(str, error="'output_name' should be a string."),
                    Optional("frontmatter"): And(bool, error="'frontmatter' should be true or false."),
                    Optional("render_content"): And(bool, error="'render_content' should be true or false."),
                    Optional("parameters"): And(
                        {str: object},
                        error="'parameters' should be a dictionary with string keys.",
                    ),
                }
            )
            init_data = schema.validate(data)
        except Exception as err:
            raise SpekulatioValidationError(f"Wrong configuration: {err}")

        # get suitable class
        try:
            module = importlib.import_module(init_data["package"])
            action_class = getattr(module, init_data["name"])
        except Exception as err:
            raise SpekulatioValidationError(
                f"Wrong action: I can't find action {init_data['name']} in package {init_data['package']}: {err}."
            )
        else:
            # remove class/package attributes before instantiating it
            del init_data["name"]
            del init_data["package"]

        # create action
        action = action_class(**init_data)

        # validate parameters
        try:
            action.validate_parameters()
        except Exception as err:
            raise SpekulatioValidationError(
                f"Wrong set of parameters for action '{action.name}': {err}"
            )

        return action

    def match(self, path: Path) -> bool:
        """Return if the provided path matches the patterns of the action."""
        is_a_match = self.parser.match(path)
        return is_a_match

    def get_output_name(self, values: dict[Any, Any]) -> str:
        """Return the output filename of the action."""

        # get output name template
        output_name = values.get("_output_name", self.output_name)

        # render template
        template = Template(output_name)
        name = template.render(values)
        if not name:
            raise SpekulatioValidationError(
                "Wrong output name for node. The output name for a node can't be an empty string. "
                f"(output name template: {output_name})."
            )
        return name

    def validate_parameters(self):
        """Validate parameter names and types.

        To be overloaded by the specific Action sub-classes.
        """
        schema = Schema({})
        schema.validate(self.parameters)

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Don't return anything by default."""
        return {}

    def process_values(self, values: dict[Any, Any]) -> dict[Any, Any]:
        """Don't modify anything by default."""
        return values

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Execute the action.

        To be overloaded by the specific Action sub-classes.
        """
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

@dataclass
class TextAction(Action):
    frontmatter: bool = False
    render_content: bool = False

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from frontmatter.

        To be overloaded by the specific Action sub-classes when they don't
        provide their values using a frontmatter.
        """
        if not self.frontmatter:
            return {"_src": input_path.read_text()}

        src, frontmatter_values = parse_values_from_frontmatter(input_path)

        values = {}
        values["_src"] = src
        values.update(frontmatter_values)
        return values

    def process_values(self, values: dict[Any, Any]) -> dict[Any, Any]:
        """Render content of the file if 'render_content' is active."""

        # skip rendering if necessary
        if not self.render_content:
            values["_content"] = values["_src"]
            return values

        # get source
        try:
            src = values["_src"]
        except KeyError:
            raise SpekulatioInternalError(
                f"Malformed action '{self.name}': it tries to make use of a '_src' value "
                "that has not been defined before."
            )

        # render template
        template = Template(src)
        content = template.render(values)

        # override src
        values["_content"] = content
        return values
