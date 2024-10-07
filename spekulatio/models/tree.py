
from dataclasses import dataclass
from .node import Node
from .layer import Layer

@dataclass
class Tree:
    root: Node

    def __init__(self, layers: list[Layer]):
        for layer in layers:
            tree.apply(layer)

    def apply(self, layer: Layer):
        """Add or override nodes for a layer."""

