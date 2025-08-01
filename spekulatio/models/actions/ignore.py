from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class Ignore(Action):
    """An action that doesn't read values or generates output."""
    process_children: ClassVar[bool] = False
    prune: ClassVar[str] = 'always'

    def match(self, root_path: Path, relative_path: Path) -> bool:
        is_a_match = self.parser.match(relative_path)
        return is_a_match
