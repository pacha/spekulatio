
from pathlib import Path
from typing import Any
from typing import Optional
from dataclasses import field
from dataclasses import dataclass
from functools import cached_property

from cels import patch_dictionary

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioValidationError
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
    _prev_sibling: Optional["Node"] = None
    _next_sibling: Optional["Node"] = None
    _sorted: bool = False

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
        # general defaults
        pre_inherited_defaults = {
            "_template": "spekulatio/default.html",
        }
        # defaults reset at each node
        post_inherited_defaults = {
            "_output_name_template": None,
            "_sort": ["*"],
        }

        effective_values = {}
        effective_values.update(pre_inherited_defaults)
        effective_values.update(self.inherited_values)
        effective_values.update(post_inherited_defaults)

        # apply patches in order: first layers first
        for layer_raw_values in self.raw_values:
            effective_values = patch_dictionary(effective_values, layer_raw_values)
        return effective_values

    @cached_property
    def user_values(self):
        """Return only user values (ie. values without leading underscore)."""
        return {key: value for key, value in self.values.items() if not key.startswith("_")}

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
    def prev_sibling(self):
        if self.is_root:
            return None
        self.parent.sort()
        return self._prev_sibling

    @cached_property
    def next_sibling(self):
        if self.is_root:
            return None
        self.parent.sort()
        return self._next_sibling

    @cached_property
    def prev(self):
        if self.is_root:
            return None
        return self.prev_sibling if self.prev_sibling else self.parent

    @cached_property
    def next(self):
        self.sort()
        if self.children:
            return list(self.children)[0]
        if self.next_sibling:
            return self.next_sibling
        if self.parent:
            return self.parent.next_sibling
        return None

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

    def sort(self):
        """Sort children.

        * The children are sorted as described in the _sort variable.
        * The _sort variable is a list of the child names.
        * All children not listed in _sort are placed alphabetically sorted
          where the special value "*" (the sink) is located in the list.
        * If the sink is not explicitly specified, it is implicitly considered
          to be at the end of the list.
        * If there are names in _sort that are not actual children of the node
          an error is raised.
        """
        # check if already sorted
        if self._sorted:
            return

        # get sorting list
        try:
            sorted_names = self.values["_sort"]
        except KeyError:
            raise SpekulatioValidationError(
                f"{self.input_path}: value '_sort' should be defined in node "
                "to be able to do traverse operations."
            )

        # validate
        all_names = set(self._children.keys())
        named_names = set(sorted_names)
        extra_names = named_names - all_names

        # duplicate entries
        if len(sorted_names) > len(named_names):
            raise SpekulatioValidationError(
                f"{self.input_path}: there are duplicated entries in the _sort list."
            )

        # wrong types
        for name in named_names:
            if not isinstance(name, str) or not name:
                raise SpekulatioValidationError(
                    f"{self.input_path}: wrong entry in _sort ('{name}'). "
                    "All values must be non-empty strings."
                )

        # non-existing entries
        if extra_names not in [set(), set("*")]:
            raise SpekulatioValidationError(
                f"{self.input_path}: names '{extra_names}' listed in _sort are not ."
                "children of the node."
            )

        # get sink position
        try:
            sink_position = sorted_names.index("*")
        except ValueError:
            sink_position = len(sorted_names)

        # sort all names
        top_names = sorted_names[:sink_position]
        bottom_names = sorted_names[(sink_position + 1):]
        missing_names = all_names - named_names
        all_sorted_names = top_names + sorted(missing_names) + bottom_names

        # sort children
        sorted_children = {}
        prev_child = None
        for name in all_sorted_names:
            child = self._children[name]
            child._prev_sibling = prev_child
            sorted_children[name] = child
            if prev_child:
                prev_child._next_sibling = child
            prev_child = child
        self._children = sorted_children

        # mark as sorted
        self._sorted = True

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
    # def __str__(self):
    #     text = f"{self.name} [{self.action.name}]"
    #     for child in self.children:
    #         text += f"\n{child.level * '-'}{child}"
    #     return text
