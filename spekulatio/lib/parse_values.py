
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

def parse_values_from_directory(path: Path, name: str):
    """Extract values from a values file."""
    if not name:
        return {}
    values_path = path / name
    if values_path.exists():
        text = values_path.read_text(encoding="utf-8")
        return yaml.safe_load(text) or {}
    return {}
