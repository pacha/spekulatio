from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class Noop(Action):
    """An action that doesn't read values or generates output."""
    process_children: ClassVar[bool] = False
    prune: ClassVar[str] = 'always'
