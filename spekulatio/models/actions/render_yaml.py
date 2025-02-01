import yaml

from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import RenderFromDataAction


@dataclass
class RenderYaml(RenderFromDataAction):
    patterns: tuple[str] = ("*.yaml", "*.yml", "*.YAML", "*.YML")
    output_name = None

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Return the content of the JSON file as values."""
        text = input_path.read_text(encoding="utf-8")
        return yaml.safe_load(text)
