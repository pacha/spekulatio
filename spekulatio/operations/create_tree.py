from spekulatio.models import Node
from spekulatio.models import Layer


def create_tree(layers: list[Layer]) -> Node:
    """Create output tree in memory from layer definitions."""
    # create root
    root = Node(name=".")

    # apply layers
    for layer in layers:
        layer.apply_to(root)

    # don't include empty directories
    root.prune()

    return root
