
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.lib.parse_values import parse_values_from_directory
from ..action import Action

@dataclass
class CreateDir(Action):

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from _values.yaml file."""
        return parse_values_from_directory(input_path)


create_dir_action = CreateDir()
