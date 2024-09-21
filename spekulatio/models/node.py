
from dataclasses import dataclass

@dataclass
class Node:
    parent: "Node" | None = None
    children: list["Node"] = []
