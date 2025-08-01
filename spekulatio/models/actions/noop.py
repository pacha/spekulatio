from typing import Any
from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class Noop(Action):
    """An action that neither reads values nor generates output."""

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Do nothing (no-operation)."""
        pass

