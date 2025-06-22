
from pathlib import Path
from dataclasses import dataclass

from .action import Action

@dataclass
class Layer:
    recipe: "Recipe"
    action: Action
    path: Path

