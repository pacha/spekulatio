from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.lib.parse_values import parse_values_from_frontmatter
from ..action import Action


@dataclass
class Render(Action):
    """Renders a text file without using a template or changing the name."""
    render_content: bool = True

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

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Render current file and write it to the output path."""

        # get source
        src = values["_action"]["src"]

        # render content
        if self.render_content:
            src_template = env.from_string(src)
            content = src_template.render(values)
        else:
            content = src

        # update values
        values["_action"]["content"] = content

        # write content
        output_path.write_text(content)
