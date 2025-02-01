from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import field
from dataclasses import dataclass

from schema import And
from schema import Schema
from schema import Optional as OptionalField

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from .node import Node
from .action import Action
from .actions import Ignore
from .actions import CreateDir


@dataclass
class Layer:
    spekulatio_file_path: Path
    path: Optional[Path]
    values_file: str
    extra_values_file: Optional[str]
    actions: list[Action] = field(default_factory=list)
    values: dict[Any, Any] = field(default_factory=dict)
    create_dir_action: CreateDir = field(init=False)

    def __post_init__(self):
        parameters = {
            "values_file": self.values_file,
            "extra_values_file": self.extra_values_file,
        }
        self.create_dir_action = CreateDir(parameters=parameters)

    @classmethod
    def from_dict(
        cls,
        spekulatio_file_path: Path,
        values_file: str,
        extra_values_file: str,
        data: dict,
        path_prefix: Path = Path("."),
    ):
        """Create an instance object from a data dictionary."""
        try:
            schema = Schema(
                {
                    OptionalField("path"): And(
                        str, len, error="'path' should be a non-empty string."
                    ),
                    OptionalField("actions"): And(
                        list, error="'actions' should be a list."
                    ),
                    OptionalField("values"): And(
                        dict, error="'values' should be a dictionary."
                    ),
                }
            )
            init_data = schema.validate(data)
        except Exception as err:
            raise SpekulatioInputError(f"Wrong configuration: {err}")

        # cast to proper types
        if "path" in init_data:
            try:
                init_data["path"] = path_prefix / Path(init_data["path"])
            except Exception as err:
                raise SpekulatioInputError(f"Invalid path '{init_data['path']}': {err}")
            if not init_data["path"].exists():
                raise SpekulatioInputError(
                    f"Can't find layer path '{init_data['path']}'"
                )
            if not init_data["path"].is_dir():
                raise SpekulatioInputError(
                    f"Layer path '{init_data['path']}' must be a directory"
                )
        else:
            # only values can be specified without a path
            extra_keys = set(init_data.keys()) - {"values"}
            if extra_keys:
                extra_keys_str = ",".join([f"'{key}'" for key in extra_keys])
                raise SpekulatioInputError(
                    f"{extra_keys_str} are specified in the layer configuration "
                    "but 'path' is missing."
                )

        if "actions" in init_data:
            actions = []
            try:
                for action_data in init_data["actions"]:
                    action = Action.from_dict(action_data)
                    actions.append(action)
                init_data["actions"] = actions
            except Exception as err:
                raise SpekulatioInputError(
                    f"Invalid action at '{spekulatio_file_path}': {err}"
                )

        return cls(
            spekulatio_file_path=spekulatio_file_path,
            values_file=values_file,
            extra_values_file=extra_values_file,
            **init_data,
        )

    def get_action(self, path: Path) -> Action:
        """Return action for a given path or None if none matches."""
        if path.is_dir():
            return self.create_dir_action
        elif path.name in (self.values_file, self.extra_values_file):
            return None
        elif path.resolve() == self.spekulatio_file_path:
            return None
        for action in self.actions:
            if action.match(path.relative_to(self.path)):
                return action
        return None

    def apply_to(self, root: Node):
        """Apply a layer to an existent tree."""

        log.debug(f"Spekulatio file: {self.spekulatio_file_path}")
        log.debug(f"Path: {self.path}")

        # add layer to root
        root._layers.append(self)
        root._actions.append(self.create_dir_action)

        # insert or update files and directories from layer
        if self.path and self.actions:
            self.apply_to_rec(node=root, path=self.path)

    def apply_to_rec(self, node: Node, path: Path):
        """Apply layer per directory, recursively."""
        for child_path in path.iterdir():
            action = self.get_action(child_path)
            if action:
                if isinstance(action, Ignore):
                    log.debug(
                        f"- {child_path} [Ignore]"
                    )
                    continue
                try:
                    child_node = node.upsert_child(
                        name=child_path.name,
                        action=action,
                        layer=self,
                    )
                except Exception as err:
                    log.exception(f"- {child_node}: {err}")
                log.debug(
                    f"- {child_node} [{str(child_node.action.__class__.__name__)}]"
                )
                if child_path.is_dir():
                    self.apply_to_rec(node=child_node, path=child_path)
