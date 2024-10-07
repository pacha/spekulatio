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
from spekulatio.exceptions import SpekulatioValidationError
from spekulatio.lib.parse_values import parse_values_from_frontmatter


@dataclass
class Action:
    patterns: tuple[str] = field(default_factory=tuple)
    output_name_template: str = "{{ _this.input_path.name }}"
    parameters: dict[str, Any] = field(default_factory=dict)
    frontmatter: bool = False
    parser: Parser = field(init=False)

    def __post_init__(self):
        self.parser = get_parser_from_list(self.patterns)

    @property
    def name(self):
        return self.__class__.__name__

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
                    Optional("output_name_template"): And(str, error="'output_name_template' should be a string."),
                    Optional("frontmatter"): And(bool, error="'frontmatter' should be true or false."),
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
        return action_class(**init_data)

    def match(self, path: Path) -> bool:
        """Return if the provided path matches the patterns of the action."""
        return self.parser.match(path)

    def get_output_name(self, values: dict[Any, Any]) -> str:
        """Return the output filename of the action."""
        output_name_template = values.get("_output_name_template", self.output_name_template)
        template = Template(output_name_template)
        output_name = template.render(values)
        return output_name

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from frontmatter and yaml files."""
        if not self.frontmatter:
            return {}
        return parse_values_from_frontmatter(input_path)

    def get_action_values(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> dict[Any, Any]:
        """Get addtional values provided by the action itself."""
        return {}

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Execute the action.

        To be overloaded by the specific Action sub-classes.
        """
        raise NotImplementedError(
            f"Malformed action '{self.__class__.__name__}': no 'execute' method defined"
        )
