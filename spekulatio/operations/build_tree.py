from pathlib import Path

from spekulatio.models import Tree
from spekulatio.models import Rule
from spekulatio.models import Layer
from spekulatio.models import Value

def build_output_tree(path: Path, rules: list[Rule], values: list[Value], layers: list[Layer]) -> Tree:
    """Built output tree in memory."""
