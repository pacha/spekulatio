from typing import Any
from pathlib import Path
from dataclasses import dataclass

from jinja2 import Template

from spekulatio.exceptions import SpekulatioInternalError
from ..action import RenderFromTextAction


@dataclass
class RenderTemplate(RenderFromTextAction):
    frontmatter: bool = True
    render_content: bool = True
    output_name = None

    def get_output_name(self, values: dict[Any, Any]) -> str:
        """Use the extension of the template if not explicit output_name template is passed."""
        if "_output_name" not in values:
            template_name = values["_template"]
            template_path = Path(template_name)
            values["_output_name"] = (
                f"{{{{ _input_name.with_suffix('{template_path.suffix}') }}}}"
            )
        return super().get_output_name(values)

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any]
    ) -> None:
        """Write file to the output path."""
        # get source
        try:
            src = values["_src"]
        except KeyError:
            raise SpekulatioInternalError(
                f"Malformed action '{self.__class__.__name__}': '_src' must be defined "
                "before calling the execute method of this class."
            )

        # get content
        if self.render_content:
            src_template = Template(src)
            content = src_template.render(values)
        else:
            content = src

        # update values
        values["_content"] = content

        # get values
        env = values["_env"]
        template_name = values["_template"]

        # render template
        template = env.get_template(template_name)
        full_content = template.render(values)

        # write content
        output_path.write_text(full_content)
