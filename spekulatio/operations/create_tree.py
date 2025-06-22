from spekulatio.models import Node
from spekulatio.models import Recipe

def create_tree(recipes: list[Recipe]) -> Node:
    """Create a representation of the file tree in memory."""
    root = Node(parent=None, name=".")
    for recipe in recipes:
        recipe.apply_to(root)
    root.prune()
    return root
