from typing import Optional
from pathlib import Path
from dataclasses import dataclass
from functools import cached_property

from schema import And
from schema import Schema
from schema import SchemaError
from schema import Optional as OptionalField
from cels import patch_dictionary

from spekulatio.logs import log
from spekulatio.paths import empty_path
from spekulatio.exceptions import SpekulatioValidationError
from .action import Action
from .actions import CreateDir
from .actions import ReadDirValues
from .layer import Layer
from .node import Node


@dataclass
class Recipe:
    input_path: Path
    actions: list
    values: dict
    values_filename: str
    recipe_path: Path

    @classmethod
    def from_dict(
        cls,
        data: dict,
        current_path: Path,
        input_path: Optional[Path],
        value_overrides: list[dict[str, object]],
        values_filename: str,
        recipe_path: Path,
    ):
        """Create object from dictionary."""

        # validate
        validated_data = cls._validate_recipe_data(data)

        # input path
        provided_input_path = data.get("input_path", input_path)
        if provided_input_path:
            actual_input_path = current_path / provided_input_path
        else:
            log.warning(
                f"No input path provided for recipe {recipe_path}. It won't generate any output."
            )
            actual_input_path = empty_path

        # actions
        actions = []
        action_definitions = data.get("actions", [])
        if action_definitions:
            for action_definition in action_definitions:
                actions.append(Action.from_dict(action_definition))

        # values
        recipe_values = data.get("values", {})
        for overrides in value_overrides:
            recipe_values = patch_dictionary(recipe_values, overrides)

        # check required values
        required_values = data.get("required_values", {})
        missing_keys = set(required_values.keys()) - set(recipe_values.keys())
        if missing_keys:
            msg = f"Missing required values for recipe {recipe_path}:\n"
            for missing_key in missing_keys:
                msg += f"- {missing_key}: {required_values[missing_key]}\n"
            raise SpekulatioValidationError(msg)

        # values_filename
        actual_values_filename = data.get("values_filename", values_filename)

        return cls(
            input_path=actual_input_path,
            actions=actions,
            values=recipe_values,
            values_filename=actual_values_filename,
            recipe_path=recipe_path,
        )

    @property
    def recipe_filename(self):
        return self.recipe_path.name

    def apply_to(self, root: Node):
        """Apply current recipe to a given root node."""

        # default actions
        root_action = ReadDirValues(values_filename=self.values_filename)
        default_dir_action = CreateDir(values_filename=self.values_filename)

        # set root layer
        layer = Layer(path=self.input_path, action=root_action, recipe=self)
        root.add_layer(layer)

        # process all other nodes
        self.apply_recursively(
            parent_path=self.input_path,
            parent_node=root,
            default_dir_action=default_dir_action,
            skip_actions=tuple(),
        )

    def apply_recursively(
        self,
        parent_path: Path,
        parent_node: Node,
        default_dir_action: Action,
        skip_actions: tuple[Action],
    ):
        for child_path in parent_path.iterdir():
            action = self._get_action(child_path, default_dir_action, skip_actions)
            if action:
                layer = Layer(path=child_path, action=action, recipe=self)
                child_node = parent_node.add_child_layer(child_path.name, layer)

                if action.process_children:
                    if action.once_per_branch:
                        skip_actions = skip_actions + (action,)
                    self.apply_recursively(child_path, child_node, default_dir_action, skip_actions)

    def _get_action(self, path: Path, default_dir_action: Action, skip_actions: tuple[Action]) -> Action:
        """Return action for a given path or None if none matches."""

        relative_path = path.relative_to(self.input_path)

        # skip Spekulatio files
        if path.name in (self.values_filename, self.recipe_filename):
            log.debug(f"- Action for {relative_path}: None (spekulatio file).")
            return None
        for action in self.actions:
            if action in skip_actions:
                continue
            if action.match(self.input_path, relative_path):
                log.debug(f"- Action for {relative_path}: {action}.")
                return action

        # default actions
        if path.is_dir():
            log.debug(f"- Action for {relative_path}: {default_dir_action} (default directory action).")
            return default_dir_action
        else:
            log.debug(f"- Action for {relative_path}: None (no match).")
            return None

    @staticmethod
    def _validate_recipe_data(data: dict) -> dict:
        """Validate recipe definition."""
        schema = Schema(
            {
                OptionalField("input_path"): And(
                    str, len, error="'input_path' should be a non-empty string."
                ),
                OptionalField("actions"): And(
                    list, error="'actions' should be a list."
                ),
                OptionalField("values"): And(
                    dict, error="'values' should be a dictionary."
                ),
                OptionalField("required_values"): And(
                    dict, error="'required_values' should be a dictionary."
                ),
                OptionalField("values_filename"): And(
                    str,
                    len,
                    error="If provided, 'values_filename' should be a non-empty string.",
                ),
            }
        )
        try:
            validated_data = schema.validate(data)
        except SchemaError as err:
            raise SpekulatioValidationError(err)
        return validated_data
