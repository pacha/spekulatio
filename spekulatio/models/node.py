
from pathlib import Path
from typing import Any
from typing import Optional
from dataclasses import field
from dataclasses import dataclass
from functools import cached_property

from cels import patch_dictionary
from jinja2 import Environment
from jinja2 import FileSystemLoader

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
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
            values = action.get_values(layer.path / self.input_file_path)
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
            "_url_prefix": "",
        }
        # defaults reset at each node
        post_inherited_defaults = {
            # "_output_name": "{{ _input_name }}",
            "_sort": ["*"],
        }

        effective_values = {}
        effective_values.update(pre_inherited_defaults)
        effective_values.update(self.inherited_values)
        effective_values.update(post_inherited_defaults)

        # apply patches in order: first layers first
        for layer_raw_values in self.raw_values:
            effective_values = patch_dictionary(effective_values, layer_raw_values)

        # add output special values
        effective_values["_root"] = self.root
        effective_values["_this"] = self
        effective_values["_input_name"] = Path(self.name)
        effective_values["_i"] = effective_values["_input_name"]
        effective_values["_env"] = self.root.env

        # add action values
        effective_values = self.action.process_values(effective_values)

        return effective_values

    @cached_property
    def user_values(self):
        """Return only user values (ie. values without leading underscore)."""
        return {key: value for key, value in self.values.items() if not key.startswith("_")}

    @cached_property
    def input_name(self):
        return self.name

    @cached_property
    def output_name(self):
        return self.action.get_output_name(self.values)

    @cached_property
    def env(self):
        template_dirs = [str(layer.path) for layer in self._layers]
        env = Environment(loader=FileSystemLoader(template_dirs))
        return env

    @cached_property
    def input_path(self):
        """Return tree path of the node (using the input names).

        Eg. /foo/bar.md
        """
        if self.is_root:
            return ""
        return f"{self.parent.input_path}/{self.input_name}"

    @cached_property
    def output_path(self):
        """Return tree path of the node (using the output names).

        Eg. /foo/bar.html
        """
        if self.is_root:
            return ""
        return f"{self.parent.output_path}/{self.output_name}"

    @cached_property
    def path(self):
        return self.input_path

    @cached_property
    def url(self):
        """Return the URL of this node."""
        url_prefix = self.values.get("_url_prefix", "")
        return f"{url_prefix}{self.output_path}"

    @cached_property
    def input_file_path(self):
        """Return the relative path of the input file in the filesystem."""
        if self.is_root:
            return Path(".")
        return self.parent.input_file_path / self.input_name

    @cached_property
    def output_file_path(self):
        """Return the relative path of the output file in the filesystem."""
        if self.is_root:
            return Path(".")
        return self.parent.output_file_path / self.output_name

    @cached_property
    def absolute_input_file_path(self):
        """Return the absolute path of the input file."""
        return (self.layer.path / self.input_file_path).absolute()

    def get_absolute_output_path(self, base_path: Path):
        """Return the absolute path of the output file."""
        return (base_path / self.output_file_path).absolute()

    @cached_property
    def level(self):
        """Return the number of nodes between this node and the root."""
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
            return self.children[0]
        if self.next_sibling:
            return self.next_sibling
        if self.parent:
            return self.parent.next_sibling
        return None

    @cached_property
    def is_root(self):
        return self.parent is None

    @cached_property
    def root(self):
        if self.is_root:
            return self
        return self.parent.root

    @cached_property
    def is_dir(self):
        return isinstance(self.action, CreateDir)

    @property
    def children(self):
        self.sort()
        return list(self._children.values())

    def __truediv__(self, other) -> "Node":
        if isinstance(other, str):
            return self.get(other)
        elif isinstance(other, self.__class__):
            return self.get(other.name)
        else:
            raise TypeError(f"Node {self.input_path} doesn't have a child {other}")

    def get(self, *path_segments: list[str]) -> "Node":
        """Return the node associated to the provided path.

        If the path is relative (eg. foo/bar.md), the node is searched from
        the current one.

        If the path is absolute (eg. /foo/bar.md), the node is searched from
        the root.
        """
        if not path_segments or path_segments == ('',):
            return self

        first_segment, tail_segments = path_segments[0], path_segments[1:]
        is_absolute_path = first_segment.startswith('/')
        if is_absolute_path:
            return self.root.get(first_segment[1:], *tail_segments)

        parts = first_segment.split('/')
        first_part, tail_parts = parts[0], parts[1:]
        try:
            child = self._children[first_part]
        except KeyError:
            raise SpekulatioInputError(f"Can't find child '{first_part}' in '{self}'.")

        return child.get(*tail_parts, *tail_segments)

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
            child = self._children[name]
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
                f"{self.absolute_input_file_path}: value '_sort' should be defined in node "
                "to be able to do traverse operations."
            )

        # validate
        all_names = set(self._children.keys())
        named_names = set(sorted_names)
        extra_names = named_names - all_names

        # duplicate entries
        if len(sorted_names) > len(named_names):
            raise SpekulatioValidationError(
                f"{self.absolute_input_file_path}: there are duplicated entries in the _sort list."
            )

        # wrong types
        for name in named_names:
            if not isinstance(name, str) or not name:
                raise SpekulatioValidationError(
                    f"{self.absolute_input_file_path}: wrong entry in _sort ('{name}'). "
                    "All values must be non-empty strings."
                )

        # non-existing entries
        if extra_names not in [set(), set("*")]:
            raise SpekulatioValidationError(
                f"{self.absolute_input_file_path}: names '{extra_names}' listed in _sort are not ."
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

    def write(self, base_path: Path) -> None:
        """Write node to disk."""
        self.action.execute(
            input_path=self.absolute_input_file_path,
            output_path=self.get_absolute_output_path(base_path),
            values=self.values
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.input_path} <{self.action}>> {self.output_path}"
