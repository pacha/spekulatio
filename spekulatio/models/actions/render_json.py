import json

from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class RenderJson(Action):
    patterns: tuple[str] = ("*.json", "*.JSON")
    output_name: Optional[str] = None

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Return the content of the JSON file as values."""
        return json.loads(input_path.read_text())

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
        """Render template by passing all values."""

        # render template
        template_name = values["_template"]
        template = env.get_template(template_name)
        rendered_content = template.render(values)

        # write content
        output_path.write_text(rendered_content)
