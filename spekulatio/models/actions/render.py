from typing import Any
from pathlib import Path
from dataclasses import dataclass

from jinja2 import Template

from spekulatio.exceptions import SpekulatioInternalError
from ..action import RenderFromTextAction


@dataclass
class Render(RenderFromTextAction):
    frontmatter: bool = True
    render_content: bool = True

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
            env = values["_env"]
            src_template = env.from_string(src)
            content = src_template.render(values)
        else:
            content = values["_src"]

        # write content
        output_path.write_text(content)
