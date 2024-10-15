import yaml
import typing
from pathlib import Path

from schema import And
from schema import Schema
from schema import Optional

from spekulatio.logs import log
from spekulatio.models import Layer
from spekulatio.lib.paths import to_relative_path
from spekulatio.exceptions import SpekulatioValidationError


def get_layers(
    spekulatio_file_path: Path,
    all_paths: typing.Optional[set[Layer]] = None,
) -> list[Layer]:
    """Get list of layers defined in a Spekulatio configuration file.

    :param spekulatio_file_path: path object to the spekulatio.yaml file.
    :param all_paths: set of paths to detect cyclic references.
    """
    layers: list[Layer] = []

    # create a set of normalized paths to detect cyclic references
    if not all_paths:
        all_paths = set()
    all_paths.add(spekulatio_file_path.resolve())

    # read file
    try:
        text = spekulatio_file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
    except Exception as err:
        raise SpekulatioValidationError(
            f"Can't read file: {err}"
        )

    # get linked layer definitions
    layer_definitions = data.pop("layers", [])
    if not isinstance(layer_definitions, list):
        raise SpekulatioValidationError(
            f"{spekulatio_file_path}: 'layers' should be a list of dictionaries."
        )

    # process each one
    schema = Schema(
        {
            "path": And(
                str, len, error="'path' in 'layers' should be a non-empty string."
            ),
        }
    )
    for layer_definition in layer_definitions:

        # get path
        try:
            validated_data = schema.validate(layer_definition)
            path = spekulatio_file_path.parent / Path(validated_data["path"])
        except Exception as err:
            raise SpekulatioValidationError(f"File {spekulatio_file_path}: {err}")

        # check that the layer file hasn't been already processed
        resolved_path = path.resolve()
        if resolved_path in all_paths:
            raise SpekulatioValidationError(
                f"File {spekulatio_file_path}: detected a cyclic dependency"
                f"{path} is included at least two times in the configuration."
            )

        # get all layers from this spekulatio file
        linked_layers = get_layers(path, all_paths)
        layers.extend(linked_layers)

    # get main layer
    if data:
        path_prefix = spekulatio_file_path.parent
        main_layer = Layer.from_dict(data, path_prefix)
        layers.append(main_layer)

    return layers
