import json

from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import RenderFromDataAction


@dataclass
class RenderJson(RenderFromDataAction):
    patterns: tuple[str] = ("*.json", "*.JSON")
    output_name = None

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Return the content of the JSON file as values."""
        return json.loads(input_path.read_text())
