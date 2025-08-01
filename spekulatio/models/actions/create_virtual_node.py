import yaml

from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError

from ..action import Action

@dataclass
class CreateVirtualNode(Action):
    patterns: tuple[str] = ("*.virt.yaml", "*.virt.yml", "*.virt.YAML", "*.virt.YML", "*.virt.json", "*.virt.JSON")
    generates_output: bool = False

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Return the content of the JSON file as values."""
        text = input_path.read_text(encoding="utf-8")
        return yaml.safe_load(text)
