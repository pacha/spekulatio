
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from jinja2 import Template

from ..action import Action

@dataclass
class Render(Action):
    frontmatter: bool = True

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Render current file and write it to the output path."""

        # when the frontmatter has been parsed, the contents of the file are
        # passed in the `_src` value. We directly read the file otherwise
        src = values.get("_src", input_path.read_text())

        # render template
        template = Template(src)
        content = template.render(values)
        output_path.write_text(content)
