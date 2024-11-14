
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from schema import Schema

from spekulatio.logs import log
from spekulatio.lib.parse_values import parse_values_from_directory
from ..action import Action

@dataclass
class CreateDir(Action):

    def validate_parameters(self):
        """Check that the provided parameters match what the action expects."""
        schema = Schema(
            {
                "values_file": str,
                "extra_values_file": [str, None],
            }
        )
        schema.validate(self.parameters)

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from a values file (eg. _values.yaml)."""
        return parse_values_from_directory(input_path, name=self.parameters['values_file'])

    def get_extra_values(self, input_path: Path) -> dict[Any, Any]:
        """Get values from an extra values file (eg. _values.dev.yaml)."""
        return parse_values_from_directory(input_path, name=self.parameters['extra_values_file'])

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Create directory."""
        output_path.mkdir(parents=False, exist_ok=True)
