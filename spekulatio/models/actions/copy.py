
import shutil
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from ..action import Action

@dataclass
class Copy(Action):

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Copy file to the output directory."""
        shutil.copy(input_path, output_path)
