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
class ReadDirValues(Action):
    values_filename: str = DEFAULT_VALUES_FILENAME
    process_children: ClassVar[bool] = True

    def match(self, root_path: Path, input_path: Path) -> bool:
        """Return if the provided path matches the patterns of the action."""
        abs_path = root_path / input_path
        return abs_path.is_dir()

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from a values file (eg. _values.yaml)."""
        return parse_values_from_file(
            directory=input_path, filename=self.values_filename
        )
