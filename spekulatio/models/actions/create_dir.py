
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log
from spekulatio.lib.parse_values import parse_values_from_directory
from ..action import Action

@dataclass
class CreateDir(Action):

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from _values.yaml file."""
        return parse_values_from_directory(input_path)

    # def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        # """Create directory."""
        # output_path.mkdir(parents=False, exist_ok=True)


create_dir_action = CreateDir()
