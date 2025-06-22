from pathlib import Path
from typing import Optional
from typing import Generator
from dataclasses import field
from dataclasses import dataclass
from functools import cached_property

from jinja2 import Environment

from cels import patch_dictionary
from py_dictfind import check

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from .layer import Layer

@dataclass
class Node:
    name: str
    parent: Optional["Node"]
    children: dict[str, "Node"] = field(default_factory=dict)
    layers: list[Layer] = field(default_factory=list)

    # sort attributes
    _sorted: bool = False
    _prev_sibling: Optional["Node"] = None
    _next_sibling: Optional["Node"] = None

    ## layers

    def add_layer(self, layer: Layer):
        self.layers.append(layer)

    def add_child_layer(self, child_name: str, layer: Layer):
        """Add a layer to a child node (create the child node first if not present)."""
        # get child
        try:
            child = self.children[child_name]
        except KeyError:
            child = self.__class__(name=child_name, parent=self)
            self.children[child_name] = child

        # add layer
        child.add_layer(layer)

        return child

    @property
    def recipe(self):
        return self.layers[-1].recipe

    @property
    def action(self):
        return self.layers[-1].action

    @property
    def path(self):
        return self.layers[-1].path

    ## input

    @property
    def input_name(self):
        return self.name

    @property
    def input_path(self):
        return self.absolute_input_path.relative_to(self.recipe.input_path)

    @property
    def absolute_input_path(self):
        return self.path

    @property
    def input_extension(self):
        return self.path.suffix

    ## output

    @cached_property
    def output_name(self):
        return self.action.get_output_name(self.values)

    @cached_property
    def output_path(self):
        """Return the relative path of the output file in the filesystem."""
        if self.is_root:
            return Path(".")
        return self.parent.output_path / self.output_name

    def get_absolute_output_path(self, base_path: Path):
        """Return the absolute path of the output file."""
        return base_path / self.output_path

    @property
    def output_extension(self):
        return self.output_path.suffix

    ## values

    @cached_property
    def values(self):
        """Compute the effective values for this node."""
        # special values
        per_branch_defaults = {
            "_template": "spekulatio/default.html",
            "_url_prefix": "",
        }
        per_node_defaults = {
            "_sort": ["*"],
        }
        per_node_extra_values = {
            "_input_path": self.absolute_input_path,
            "_node": self,
            "_root": self.root,
        }

        value_dicts = []  # values in the order that have to be applied

        # branch default values
        value_dicts.append(per_branch_defaults)

        # parent values
        if self.is_root:
            value_dicts.extend([layer.recipe.values for layer in self.layers])
        else:
            value_dicts.append(self.parent.values)

        # per-node default values
        value_dicts.append(per_node_defaults)

        # layer values
        value_dicts.extend([layer.action.get_values(input_path=layer.path) for layer in self.layers])

        # overriding special values
        value_dicts.append(per_node_extra_values)

        # merge values
        effective_values = {}
        for value_dict in value_dicts:
            effective_values = patch_dictionary(effective_values, value_dict)

        return effective_values

    @property
    def user_values(self):
        """Return only user values (ie. values without leading underscore)."""
        return {
            key: value for key, value in self.values.items() if not key.startswith("_")
        }

    ## sorting

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
            sorting_list = self.values["_sort"]
        except KeyError:
            raise SpekulatioInputError(
                f"{self}: value '_sort' should be defined "
                "to be able to do traverse operations."
            )

        # get names to sort
        all_names = set(self.children.keys())
        deduplicated_sorting_list = set(sorting_list)
        extra_names = deduplicated_sorting_list - all_names

        # check duplicate entries
        if len(sorting_list) > len(deduplicated_sorting_list):
            raise SpekulatioInputError(
                f"{self}: there are duplicated entries in the _sort list."
            )

        # check wrong types
        for name in deduplicated_sorting_list:
            if not isinstance(name, str) or not name:
                raise SpekulatioInputError(
                    f"{self}: wrong entry in _sort ('{name}'). "
                    "All values must be non-empty strings."
                )

        # check non-existing entries
        if extra_names not in [set(), set("*")]:
            raise SpekulatioInputError(
                f"{self}: names '{extra_names}' listed in _sort are not ."
                "children of the node."
            )

        # get sink position
        try:
            sink_position = sorting_list.index("*")
        except ValueError:
            sink_position = len(sorting_list)

        # sort all names
        top_names = sorting_list[:sink_position]
        bottom_names = sorting_list[(sink_position + 1) :]
        missing_names = all_names - deduplicated_sorting_list
        all_sorted_names = top_names + sorted(missing_names) + bottom_names

        # sort children
        sorted_children = {}
        prev_child = None
        for name in all_sorted_names:
            child = self.children[name]
            child._prev_sibling = prev_child
            sorted_children[name] = child
            if prev_child:
                prev_child._next_sibling = child
            prev_child = child
        if all_sorted_names:
            child._next_sibling = None

        # set overriden unsorted children dictionary
        self.children = sorted_children

        # mark as sorted
        self._sorted = True

    ## relations

    @property
    def is_root(self):
        return self.parent is None

    @cached_property
    def root(self):
        if self.is_root:
            return self
        return self.parent.root

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
            return next(iter(self.children.values()))
        return self._next_ancestor_sibling

    @cached_property
    def _next_ancestor_sibling(self):
        self.sort()
        if self.next_sibling:
            return self.next_sibling
        else:
            return self.parent._next_ancestor_sibling if self.parent else None

    @property
    def sorted_children(self):
        self.sort()
        yield from self.children.values()

    ## basic features

    @cached_property
    def is_directory(self):
        return self.absolute_input_path.is_dir()

    @cached_property
    def level(self):
        """Return the number of nodes between this node and the root."""
        if self.is_root:
            return 0
        return self.parent.level + 1

    @cached_property
    def title(self):
        try:
            return self.values["_title"]
        except KeyError:
            path_stem = self.input_path.stem
            with_spaces = path_stem.replace("-", " ").replace("_", " ")
            result = words.title()
            return result

    @cached_property
    def url(self):
        """Return the URL of this node."""
        url_prefix = self.values.get("_url_prefix", "")
        path_str = "" if self.is_root else str(self.output_path)
        return f"{url_prefix}/{path_str}"

    ## traversing

    def get(self, *path_segments: list[str]) -> "Node":
        """Return the node associated to the provided path.

        If the path is relative (eg. foo/bar.md), the node is searched from
        the current one.

        If the path is absolute (eg. /foo/bar.md), the node is searched from
        the root.
        """
        if not path_segments or path_segments == ("",):
            return self

        first_segment, tail_segments = path_segments[0], path_segments[1:]
        is_absolute_path = first_segment.startswith("/")
        if is_absolute_path:
            return self.root.get(first_segment[1:], *tail_segments)

        parts = first_segment.split("/")
        first_part, tail_parts = parts[0], parts[1:]
        try:
            child = self.children[first_part]
        except KeyError:
            raise SpekulatioInputError(f"Can't find child '{first_part}' in '{self}'.")

        return child.get(*tail_parts, *tail_segments)

    def find(self, condition: str, unsorted=False) -> Generator["Node", None, None]:
        """Yield all descendants that fulfill the given condition."""
        for node in self.traverse(unsorted=unsorted):
            if check(node.values, condition):
                yield node

    def __truediv__(self, other) -> "Node":
        """Overload / operator.

        `node / "some-file.md"` is the same as `node.get("some-file.md")`.
        """
        if isinstance(other, str):
            return self.get(other)
        elif isinstance(other, self.__class__):
            return self.get(other.name)
        else:
            raise TypeError(f"Node {self.input_path} doesn't have a child {other}")

    def traverse(self, unsorted=False) -> Generator["Node", None, None]:
        if not unsorted:
            self.sort()
        for child in self.children.values():
            yield child
            yield from child.traverse(unsorted=unsorted)

    def traverse_post_order(self):
        """Traverse visiting the leaves first without ensuring order."""
        result = []
        for child in self.children.values():
            result.extend(child.traverse_post_order())
        result.append(self)
        return result

    ## prune

    def prune(self):
        """Remove all invalid descendants."""
        # all nodes must me stored in a list so that the tree doesn't mutate during traversing
        for node in self.traverse_post_order():

            if node.is_root:
                break

            fails_action_condition = not node._meets_action_condition()
            empty_directory = node.is_directory and not node.children

            if fails_action_condition or empty_directory:
                reason = "empty directory" if empty_directory else "fails action condition"
                log.info(f"Pruning directory '{node}': {reason}.")
                del node.parent.children[node.name]
                node.parent = None

    def _meets_action_condition(self):
        """Return if the current node meets its action condition."""
        if not self.layers or not self.action.condition:
            return True
        return self.action.check_condition(self.values)

    ## writing

    def write(self, base_output_path: Path, cache: bool, env: Environment) -> None:
        """Write node to disk.

        :base_path: root of the output path
        :cache: don't write the file if it exists and its output timestamp is
            newer than the update timestamp of the input file.
        """
        abs_input_path = self.absolute_input_path
        abs_output_path = self.get_absolute_output_path(base_output_path)

        # skip if file is cached
        if cache and abs_output_path and abs_output_path.exists():
            input_timestamp = abs_input_path.stat().st_mtime
            output_timestamp = abs_output_path.stat().st_mtime
            if output_timestamp > input_timestamp:
                log.info(f"- {self} (Cached)")
                return

        # execute action
        log.info(f"- {self} [{self.action}]")
        try:
            self.action.execute(
                input_path=abs_input_path, output_path=abs_output_path, values=self.values, env=env
            )
        except Exception as err:
            raise Exception(f"Error {self}: {err}") from err

    def __repr__(self):
        return f"<Node: {self.input_path}>"

    def __str__(self):
        return str(self.input_path)

