
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from ..action import RenderFromTextAction

@dataclass
class Render(RenderFromTextAction):
    frontmatter: bool = True
    render_content: bool = True

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Write file to the output path."""
        content = values["_content"]
        output_path.write_text(content)
