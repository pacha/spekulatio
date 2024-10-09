
import yaml
import json
from pathlib import Path
from typing import Dict, Callable

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioValidationError
from .parse_frontmatter import parse_frontmatter

def parse_values_from_frontmatter(path: Path):
    """Extract frontmatter values from the given path."""
    text = path.read_text(encoding="utf-8")
    _, values = parse_frontmatter(text)
    return values

def parse_values_from_directory(path: Path, name: str = '_values'):
    """Extract values from a values file."""
    if not path.is_dir():
        raise SpekulatioValidationError(f"{path} is not a directory.")

    variants = [
        (f"{name}.yaml", "yaml"),
        (f"{name}.yml", "yaml"),
        (f"{name}.YAML", "yaml"),
        (f"{name}.YML", "yaml"),
        (f"{name}.json", "json"),
        (f"{name}.JSON", "json"),
    ]
    load_functions: Dict[str, Callable] = {
        "yaml": yaml.safe_load,
        "json": json.loads,
    }

    for variant, filetype in variants:
        values_path = path / variant
        if values_path.exists():
            load_function = load_functions[filetype]
            text = values_path.read_text(encoding="utf-8")
            return load_function(text) or {}
    return {}
