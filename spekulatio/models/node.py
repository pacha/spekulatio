
from typing import Optional
from dataclasses import field
from dataclasses import dataclass

@dataclass
class Node:
    parent: Optional["Node"] = None
    children: list["Node"] = field(default_factory=list)
