
from dataclasses import dataclass
from .node import Node

@dataclass
class Tree:
    root: Node

    def __init__(self, root: Node):
        self.root = root
