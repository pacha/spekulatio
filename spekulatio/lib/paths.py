
from pathlib import Path

def to_relative_path(path_str: str) -> Path:
    """Convert a string that contains a path into a relative path.

    Eg. "foo/bar" -> Path("foo/bar")
        "/foo/bar" -> Path("foo/bar")
        "." -> Path(".")
    """
    path = Path(path_str)
    if path.is_absolute():
        root = Path(Path().resolve().anchor)
        path = path.relative_to(root)
    return path
