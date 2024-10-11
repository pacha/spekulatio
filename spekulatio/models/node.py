
from pathlib import Path
from typing import Any
from typing import Optional
from dataclasses import field
from dataclasses import dataclass
from functools import cached_property

from cels import patch_dictionary


from spekulatio.logs import log
from .action import Action
from .actions import CreateDir


@dataclass
class Node:

    name: str
    _layers: list["Layer"] = field(default_factory=list)
    _values: list[dict[Any, Any]] = field(default_factory=list)
    _actions: list[Action] = field(default_factory=list)
    _children: dict[str, "Node"] = field(default_factory=dict)

    # links
    parent: Optional["Node"] = None
    prev: Optional["Node"] = None
    next: Optional["Node"] = None
    prev_sibling: Optional["Node"] = None
    next_sibling: Optional["Node"] = None

    @cached_property
    def raw_values(self) -> list[dict[Any, Any]]:
        """Collect raw values from layers.

        Raw values will be cached in `_raw_values`.
        """
        if self._values:
            return self._values

        for layer, action in zip(self._layers, self._actions):
            values = action.get_values(layer.path / self.path)
            self._values.append(values)
        return self._values

    @cached_property
    def layer_values(self) -> list[dict[Any, Any]]:
        """Collect values layer definitions."""
        values = {}
        for layer in self._layers:
            values = patch_dictionary(values, layer.values)
        return values

    @cached_property
    def inherited_values(self):
        """Return the values that come from ancestors."""
        return self.layer_values if self.is_root else self.parent.values

    @cached_property
    def values(self):
        """Compute the effective values for this node."""
        effective_values = {}
        effective_values.update(self.inherited_values)

        # apply patches in order: first layers first
        for layer_raw_values in self.raw_values:
            effective_values = patch_dictionary(effective_values, layer_raw_values)
        return effective_values

    @cached_property
    def path(self):
        if self.is_root:
            return Path(".")
        return self.parent.path / self.name

    @cached_property
    def level(self):
        if self.is_root:
            return 0
        return self.parent.level + 1

    @cached_property
    def action(self):
        return self._actions[-1]

    @cached_property
    def layer(self):
        return self._layers[-1]

    @cached_property
    def input_path(self):
        if self.is_root:
            return Path(".")
        return self.layer.path / self.path

    @cached_property
    def children(self):
        return self._children.values()

    @cached_property
    def is_root(self):
        return self.parent is None

    @cached_property
    def is_dir(self):
        return isinstance(self.action, CreateDir)

    def __getitem__(self, name) -> "Node":
        """Get child by name.

        Eg. node['path']['to']['other']['node']
        """
        return self._children[name]

    def get_child(self, name: str) -> "Node":
        """Get child by name."""
        return self[name]

    def _insert_child(self, name: str) -> "Node":
        """Add new child to node."""
        child = Node(name=name)
        self._children[name] = child
        child.parent = self
        return child

    def upsert_child(self, name: str, action: Action, layer: "Layer") -> "Node":
        """Insert or update child."""
        try:
            # child exists
            child = self.get_child(name)
        except KeyError:
            # child doesn't exist yet
            child = self._insert_child(name=name)
        finally:
            child._layers.append(layer)
            child._actions.append(action)
        return child

    def traverse(self):
        """Retrieve all descendants of this node."""
        for child in self.children:
            yield child
            yield from child.traverse()

    def prune(self):
        """Remove branches that don't end in a file."""
        for child in list(self.children):
            child.prune()
            if not child._children and child.is_dir:
                del self._children[child.name]
                child.parent = None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
    # def __str__(self):
    #     text = f"{self.name} [{self.action.name}]"
    #     for child in self.children:
    #         text += f"\n{child.level * '-'}{child}"
    #     return text
