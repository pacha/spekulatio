import importlib
from typing import Any
from typing import Optional
from typing import Callable
from typing import ClassVar
from pathlib import Path
from dataclasses import field
from dataclasses import dataclass

from schema import And
from schema import Schema
from schema import SchemaError
from schema import Optional as OptionalField
from jinja2 import Template
from py_walk import get_parser_from_list
from py_walk.models.parser import Parser
from py_dictfind import get_checker

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from spekulatio.exceptions import SpekulatioValidationError


@dataclass
class Action:
    patterns: tuple[str] = field(default_factory=tuple)
    output_name: str = "{{ _input_path.name }}"
    parameters: dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    render_content: bool = False
    parser: Parser = field(init=False)
    check_condition: Optional[Callable] = field(init=False)
    process_children: ClassVar[bool] = False  # whether children are processed if matched
    once_per_branch: ClassVar[bool] = False  # whether children can match this action if an ancestor was matched
    prune: ClassVar[str] = 'never'  # options: never, if-no-children, always
    generates_output: bool = True  # some actions only read data but doesn't generate any output file or directory

    def __post_init__(self):
        self.parser = get_parser_from_list(self.patterns)
        self.check_condition = get_checker(self.condition) if self.condition else None

    @classmethod
    def from_dict(cls, data):
        """Create an instance object from a data dictionary."""
        # validate
        schema = Schema(
            {
                "name": And(str, error="'name' should be a string."),
                OptionalField("package", default="spekulatio"): And(
                    str, error="'package' should be a string."
                ),
                OptionalField("patterns"): And(
                    [str], error="'patterns' should be a list of strings."
                ),
                OptionalField("output_name"): And(
                    str, error="'output_name' should be a string."
                ),
                OptionalField("parameters"): And(
                    {str: object},
                    error="'parameters' should be a dictionary with string keys.",
                ),
                OptionalField("condition"): And(
                    str, error="'condition' should be a string."
                ),
                OptionalField("render_content"): And(
                    bool, error="'render_content' should be a boolean value."
                ),
            }
        )
        try:
            init_data = schema.validate(data)
        except SchemaError as err:
            raise SpekulatioValidationError(err)

        # get suitable class
        try:
            module = importlib.import_module(init_data["package"])
            action_class = getattr(module, init_data["name"])
        except Exception:
            raise SpekulatioInputError(
                f"Can't find action '{init_data['name']}' in package '{init_data['package']}'."
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
            raise SpekulatioInputError(
                f"Wrong set of parameters for action '{action}': {err}"
            )

        return action

    @classmethod
    def name(cls):
        return cls.__name__

    def match(self, root_path: Path, relative_path: Path) -> bool:
        """Return if the provided path matches the patterns of the action. """
        absolute_path = root_path / relative_path
        # don't match directories by default
        if absolute_path.is_dir():
            return False
        is_a_match = self.parser.match(relative_path)
        return is_a_match

    def get_output_name(self, values: dict[Any, Any], output_name: Optional[str] = None) -> str:
        """Return the output filename of the action."""
        output_name_template = values.get("_output_name") or output_name or self.output_name
        template = Template(output_name_template)
        name = template.render(values)
        if not name:
            raise SpekulatioInputError(
                "Wrong output name for node. The output name for a node can't be an empty string. "
                f"(output name template: {output_name_template})."
            )
        return name

    ## most common methods to override

    def validate_parameters(self):
        """Validate parameter names and types.

        To be overloaded by the specific Action sub-classes. No validation by default.

        Raise ValueError to indicate
        """
        pass

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Don't return anything by default."""
        return {}

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Execute the action.

        To be overloaded by the specific Action sub-classes.
        """
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"[{self.name()}]"

