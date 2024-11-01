import importlib
from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import field
from dataclasses import dataclass

from schema import And
from schema import Schema
from schema import Optional as OptionalField
from jinja2 import Template
from py_walk import get_parser_from_list
from py_walk.models.parser import Parser

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.exceptions import SpekulatioInputError
from spekulatio.lib.parse_values import parse_values_from_frontmatter


@dataclass
class Action:
    patterns: tuple[str] = field(default_factory=tuple)
    output_name: Optional[str] = "{{ _input_name }}"
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
                    OptionalField("package", default="spekulatio"): And(str, error="'package' should be a string."),
                    OptionalField("patterns"): And([str], error="'patterns' should be a list of strings."),
                    OptionalField("output_name"): And(str, error="'output_name' should be a string."),
                    OptionalField("frontmatter"): And(bool, error="'frontmatter' should be true or false."),
                    OptionalField("render_content"): And(bool, error="'render_content' should be true or false."),
                    OptionalField("parameters"): And(
                        {str: object},
                        error="'parameters' should be a dictionary with string keys.",
                    ),
                }
            )
            init_data = schema.validate(data)
        except Exception as err:
            raise SpekulatioInputError(f"Wrong configuration: {err}")

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
        if not output_name:
            raise SpekulatioInputError(
                f"You need to set 'output_name' to use the '{self.__class__.__name__}' action."
            )

        # render template
        template = Template(output_name)
        name = template.render(values)
        if not name:
            raise SpekulatioInputError(
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
class RenderFromTextAction(Action):
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


@dataclass
class RenderFromDataAction(Action):
    output_name: Optional[str] = None

    def get_output_name(self, values: dict[Any, Any]) -> str:
        """Use the extension of the template if not explicit output_name template is passed."""
        if "_output_name" not in values:
            template_name = values["_template"]
            template_path = Path(template_name)
            values["_output_name"] = f"{{{{ _input_name.with_suffix('{template_path.suffix}') }}}}"
        return super().get_output_name(values)

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Render template by passing all values."""

        # get values
        env = values["_env"]
        template_name = values["_template"]

        # render template
        template = env.get_template(template_name)
        rendered_content = template.render(values)

        # write content
        output_path.write_text(rendered_content)
