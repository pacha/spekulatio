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
    recipe_filename: str

    @classmethod
    def from_dict(
        cls,
        data: dict,
        current_path: Path,
        input_path: Optional[Path],
        value_overrides: list[dict[str, object]],
        values_filename: str,
        recipe_filename: str,
    ):
        """Create object from dictionary."""

        # validate
        validated_data = cls._validate_recipe_data(data)

        # input path
        provided_input_path = data.get("input_path", input_path)
        actual_input_path = (current_path / provided_input_path) if provided_input_path else empty_path

        # actions
        action_definitions = data.get("actions", [])
        if action_definitions:
            # creating directories is always the first action (to be re-assessed in the future)
            actions = [CreateDir(values_filename=values_filename)]
            for action_definition in action_definitions:
                actions.append(Action.from_dict(action_definition))
        else:
            actions = []

        # values
        recipe_values = data.get("values", {})
        for overrides in value_overrides:
            recipe_values = patch_dictionary(recipe_values, overrides)

        # values_filename
        actual_values_filename = data.get("values_filename", values_filename)

        # input path
        return cls(
            input_path=actual_input_path,
            actions=actions,
            values=recipe_values,
            values_filename=actual_values_filename,
            recipe_filename=recipe_filename,
        )

    def apply_to(self, root: Node):
        layer = Layer(path=self.input_path, action=ReadDirValues(values_filename=self.values_filename),  recipe=self)
        root.add_layer(layer)
        self.apply_recursively(parent_path=self.input_path, parent_node=root)

    def apply_recursively(self, parent_path: Path, parent_node: Node):
        for child_path in parent_path.iterdir():
            action = self._get_action(child_path)
            if action:
                layer = Layer(path=child_path, action=action, recipe=self)
                child_node = parent_node.add_child_layer(child_path.name, layer)

                if action.process_children:
                    self.apply_recursively(child_path, child_node)

    def _get_action(self, path: Path) -> Action:
        """Return action for a given path or None if none matches."""
        # skip Spekulatio files
        if path.name in (self.values_filename, self.recipe_filename):
            return None
        for action in self.actions:
            if action.match(path):
                return action
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
                OptionalField("values_filename"): And(
                    str, len, error="If provided, 'values_filename' should be a non-empty string."
                ),
            }
        )
        try:
            validated_data = schema.validate(data)
        except SchemaError as err:
            raise SpekulatioValidationError(err)
        return validated_data

