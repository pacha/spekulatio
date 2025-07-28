import shutil
from typing import Any
from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass

from spekulatio.exceptions import SpekulatioInputError
from ..action import Action


@dataclass
class Copy(Action):
    process_children: ClassVar[bool] = False
    prune: ClassVar[str] = 'never'

    def validate_parameters(self):
        """This action takes no parameters."""
        if self.parameters:
            raise SpekulatioInputError(
                f"Action {self} takes no parameters."
            )

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Copy file to the output directory."""
        shutil.copy(input_path, output_path)
