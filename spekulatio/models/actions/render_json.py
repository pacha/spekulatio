
import json

from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action

@dataclass
class RenderJson(Action):
    patterns: tuple[str] = ("*.json", "*.JSON")
    output_name = None

    def get_output_name(self, values: dict[Any, Any]) -> str:
        """Use the extension of the template if not explicit output_name template is passed."""
        if "_output_name" not in values:
            template_name = values["_template"]
            template_path = Path(template_name)
            values["_output_name"] = f"{{{{ _input_name.with_suffix('{template_path.suffix}') }}}}"
        return super().get_output_name(values)

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Return the content of the JSON file as values."""
        return json.loads(input_path.read_text())

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
