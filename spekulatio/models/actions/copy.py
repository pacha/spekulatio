
import shutil
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from ..action import Action

@dataclass
class Copy(Action):

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Copied files don't define extra values."""
        return {}

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Copy file to the output directory."""
        shutil.copy(input_path, output_path)
