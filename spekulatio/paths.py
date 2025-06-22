import os
from pathlib import Path

from .lib.paths import get_paths_from_env_var
from .exceptions import SpekulatioInputError

DEFAULT_SPEKULATIO_FILENAME = "spekulatio.yaml"
DEFAULT_VALUES_FILENAME = "_values.yaml"
SPEKULATIO_PATH_ENV_VAR_NAME = "SPEKULATIO_PATH"

project_path = Path(__file__).parent.absolute()
default_template_path = project_path / "data" / "templates"
default_recipe_path = project_path / "data" / "recipes"
empty_path = project_path / "data" / "empty"
search_recipe_paths = get_paths_from_env_var(SPEKULATIO_PATH_ENV_VAR_NAME) + [default_recipe_path]

