from dataclasses import dataclass

from ..action import Action


@dataclass
class Ignore(Action):
    pass
