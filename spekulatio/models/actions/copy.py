
import shutil
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from spekulatio.exceptions import SpekulatioInputError
from ..action import Action

@dataclass
class Copy(Action):

    def validate_parameters(self):
        """This action takes no parameters."""
        if self.parameters:
            raise SpekulatioInputError(f"Action {self.__class__.__name__} takes no parameters.")

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Copy file to the output directory."""
        shutil.copy(input_path, output_path)
