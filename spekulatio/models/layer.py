from dataclasses import field
from dataclasses import dataclass
from typing import Any
from pathlib import Path

from schema import And
from schema import Schema
from schema import Optional

from spekulatio.lib.paths import to_relative_path
from spekulatio.exceptions import SpekulatioValidationError
from .node import Node
from .action import Action
from .actions import noop_action
from .actions import create_dir_action


@dataclass
class Layer:
    spekulatio_file_path: Path
    path: Path
    values_file: str = "_values.yaml"
    actions: list[Action] = field(default_factory=list)
    values: dict[Any, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        spekulatio_file_path: Path,
        data: dict,
        path_prefix: Path = Path("."),
    ):
        """Create an instance object from a data dictionary."""
        try:
            schema = Schema(
                {
                    Optional("path"): And(
                        str, len, error="'path' should be a non-empty string."
                    ),
                    Optional("values_file"): And(
                        str, len, error="'values_file' should be a non-empty string."
                    ),
                    Optional("actions"): And(list, error="'actions' should be a list."),
                    Optional("values"): And(
                        dict, error="'values' should be a dictionary."
                    ),
                }
            )
            init_data = schema.validate(data)
        except Exception as err:
            raise SpekulatioValidationError(f"Wrong configuration: {err}")

        # cast to proper types
        if "path" in init_data:
            try:
                init_data["path"] = path_prefix / Path(init_data["path"])
            except Exception as err:
                raise SpekulatioValidationError(
                    f"Invalid path '{init_data['path']}': {err}"
                )
            if not init_data["path"].exists():
                raise SpekulatioValidationError(
                    f"Can't find layer path '{init_data['path']}'"
                )
            if not init_data["path"].is_dir():
                raise SpekulatioValidationError(
                    f"Layer path '{init_data['path']}' must be a directory"
                )
        else:
            init_data["path"] = path_prefix / Path(".")

        if "actions" in init_data:
            actions = []
            try:
                for action_data in init_data["actions"]:
                    action = Action.from_dict(action_data)
                    actions.append(action)
                init_data["actions"] = actions
            except Exception as err:
                raise SpekulatioValidationError(f"Invalid action: {err}")

        return cls(spekulatio_file_path=spekulatio_file_path, **init_data)

    def get_action(self, path: Path) -> Action:
        """Return action for a given path or None if none matches."""
        if path.is_dir():
            return create_dir_action
        elif path.name == self.values_file:
            return None
        elif path.resolve() == self.spekulatio_file_path:
            return None
        for action in self.actions:
            if action.match(path.relative_to(self.path)):
                return action
        return None

    def apply_to(self, root: Node):
        """Apply a layer to an existent tree."""

        # add layer to root
        root._layers.append(self)
        root._actions.append(create_dir_action)

        # insert or update files and directories from layer
        self.apply_to_rec(node=root, path=self.path)

    def apply_to_rec(self, node: Node, path: Path):
        """Apply layer per directory, recursively."""
        for child_path in path.iterdir():
            action = self.get_action(child_path)
            if action:
                child_node = node.upsert_child(
                    name=child_path.name,
                    action=action,
                    layer=self,
                )
                if child_path.is_dir():
                    self.apply_to_rec(node=child_node, path=child_path)
