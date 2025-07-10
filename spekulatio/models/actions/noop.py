from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class Noop(Action):
    """An action that doesn't read values or generates output."""

    def match(self, input_path: Path) -> bool:
        """Return if the provided path matches the patterns of the action."""
        is_a_match = self.parser.match(input_path)
        return is_a_match
