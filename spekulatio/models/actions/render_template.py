from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from jinja2 import Template

from spekulatio.exceptions import SpekulatioInputError
from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.lib.parse_values import parse_values_from_frontmatter
from ..action import Action


@dataclass
class RenderTemplate(Action):
    render_content: bool = True
    output_name: Optional[str] = None

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Parse frontmatter if present."""
        src, frontmatter_values = parse_values_from_frontmatter(input_path)
        values = {
            "_action": {
                "src": src,
            }
        }
        values.update(frontmatter_values)
        return values

    def get_output_name(self, values: dict[Any, Any], output_name: Optional[str] = None) -> str:
        """Use the extension of the template if not explicit output_name template is passed."""
        if self.output_name:
            new_output_name = self.output_name
        else:
            template_name = values["_template"]
            template_path = Path(template_name)
            template_suffix = template_path.suffix
            new_output_name = f"{{{{ _input_path.with_suffix('{template_suffix}').name }}}}"
        return super().get_output_name(values, output_name=new_output_name)

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Render current file and write it to the output path."""

        # get source
        src = values["_action"]["src"]

        # get content
        if self.render_content:
            src_template = Template(src)
            content = src_template.render(values)
        else:
            content = src

        # update values
        values["_action"]["content"] = content

        # render template
        try:
            template_name = values["_template"]
        except KeyError:
            raise SpekulatioInputError(f"Action '{self}' can't be used if the value _template is not defined")
        template = env.get_template(template_name)
        rendered_content = template.render(values)

        # write content
        output_path.write_text(rendered_content)
