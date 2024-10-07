
from dataclasses import dataclass

from ..action import Action

@dataclass
class NoOp(Action):
    pass

noop_action = NoOp()
