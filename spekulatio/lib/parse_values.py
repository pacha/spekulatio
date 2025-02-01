import yaml
import json
from pathlib import Path
from typing import Dict, Callable

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from .parse_frontmatter import parse_frontmatter


def parse_values_from_frontmatter(path: Path):
    """Extract frontmatter values from the given path."""
    text = path.read_text(encoding="utf-8")
    src, values = parse_frontmatter(text)
    return src, values


def parse_values_from_file(directory: Path, filename: str, fail_if_missing=False):
    """Extract values from a values file."""
    if not filename:
        return {}
    values_path = directory / filename
    if values_path.exists():
        text = values_path.read_text(encoding="utf-8")
        values = yaml.safe_load(text) or {}
        if not isinstance(values, dict):
            raise ValueError(f"Values can only be provided as a dictionary or map.")
        return values
    else:
        if fail_if_missing:
            raise FileNotFoundError(f"Can't find {values_path}.")
    return {}

def parse_values_from_string(values_str: str):
    """Extract values from a values string."""
    values = yaml.safe_load(values_str) or {}
    if not isinstance(values, dict):
        raise ValueError(f"Values can only be provided as a dictionary or map.")
    return values
