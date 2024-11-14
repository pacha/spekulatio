import yaml
from typing import Optional
from pathlib import Path

from schema import And
from schema import Schema

from spekulatio.logs import log
from spekulatio.models import Layer
from spekulatio.paths import default_layers_path
from spekulatio.exceptions import SpekulatioInputError


SPEKULATIO_FILE = "spekulatio.yaml"

def get_layers(
    input_path: Path,
    values_file: str = "_values.yaml",
    extra_values_file: Optional[str] = None,
    base_path: Optional[Path] = None,
    all_paths: Optional[set[Layer]] = None,
) -> list[Layer]:
    """Get list of layers defined in a Spekulatio configuration file.

    :param spekulatio_file_path: path object to the spekulatio.yaml file.
    :param all_paths: set of paths to detect cyclic references.
    """
    layers: list[Layer] = []

    # determine actual spekulatio file path
    # (in case the user pased just a directory or we have to check the default layers path)
    user_provided_path = base_path / input_path if base_path else input_path
    fallback_path = default_layers_path / input_path

    paths = [
        user_provided_path,
        user_provided_path / SPEKULATIO_FILE,
        fallback_path,
        fallback_path / SPEKULATIO_FILE,
    ]
    for path in paths:
        if path.is_file():
            spekulatio_file_path = path
            break
    else:
        raise SpekulatioInputError(
            f"Can't find configuration file at '{user_provided_path}'."
        )

    # create a set of spekulatio file paths to detect cyclic references
    if not all_paths:
        all_paths = set()
    all_paths.add(spekulatio_file_path.resolve())

    # read file
    try:
        text = spekulatio_file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
    except Exception as err:
        raise SpekulatioInputError(
            f"Can't read configuration file: {err}"
        )

    # get linked layer definitions
    layer_definitions = data.pop("layers", [])
    if not isinstance(layer_definitions, list):
        raise SpekulatioInputError(
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
            base_path = spekulatio_file_path.parent
            input_path = Path(validated_data["path"])
        except Exception as err:
            raise SpekulatioInputError(f"File {spekulatio_file_path}: {err}")

        # check that the layer file hasn't been already processed
        full_path = (base_path / input_path).resolve()
        if full_path in all_paths:
            raise SpekulatioInputError(
                f"File {spekulatio_file_path}: detected a cyclic dependency"
                f"{full_path} is included at least two times in the configuration."
            )

        # get all layers from this spekulatio file
        linked_layers = get_layers(input_path, values_file, extra_values_file, base_path, all_paths)
        layers.extend(linked_layers)

    # get main layer
    if data:
        path_prefix = spekulatio_file_path.parent
        main_layer = Layer.from_dict(spekulatio_file_path, values_file, extra_values_file, data, path_prefix)
        layers.append(main_layer)

    return layers
