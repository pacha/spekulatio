from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action


@dataclass
class Noop(Action):
    """An action that doesn't read values or generates output."""
    pass
