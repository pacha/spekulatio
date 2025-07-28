from typing import Any
from typing import ClassVar
from pathlib import Path
from dataclasses import dataclass

from schema import Schema

from spekulatio.logs import log
from spekulatio.paths import DEFAULT_VALUES_FILENAME
from spekulatio.lib.parse_values import parse_values_from_file
from ..action import Action


@dataclass
class CreateDir(Action):
    values_filename: str = DEFAULT_VALUES_FILENAME
    process_children: ClassVar[bool] = True
    prune: ClassVar[str] = 'if-no-children'

    def match(self, root_path: Path, relative_path: Path) -> bool:
        absolute_path = root_path / relative_path
        return absolute_path.is_dir()

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from a values file (eg. _values.yaml)."""
        return parse_values_from_file(
            directory=input_path, filename=self.values_filename
        )

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Create directory."""
        output_path.mkdir(parents=False, exist_ok=True)
