
import difflib
from pathlib import Path
from typing import Optional

def get_unified_diff(
    path1: Path, 
    path2: Path, 
    context_lines: int = 3,
    encoding: str = 'utf-8',
    fromfile: Optional[str] = None,
    tofile: Optional[str] = None
) -> str:
    """
    Compare two files and return their unified diff as a string.
    
    Args:
        path1: First file path
        path2: Second file path
        context_lines: Number of context lines to show around changes
        encoding: File encoding to use when reading files
        fromfile: Custom label for the first file (defaults to path1)
        tofile: Custom label for the second file (defaults to path2)

    Returns:
        String containing the unified diff, or empty string if files are identical

    Raises:
        FileNotFoundError: If either file doesn't exist
        UnicodeDecodeError: If files contain binary data that can't be decoded
        PermissionError: If files can't be read due to permissions
    """
    # Read the files
    try:
        with path1.open('r', encoding=encoding) as f1:
            lines1 = f1.readlines()
        with path2.open('r', encoding=encoding) as f2:
            lines2 = f2.readlines()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Cannot decode file as {encoding}. Files may be binary."
        ) from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading files") from e

    # Use custom labels or default to file paths
    from_label = fromfile or str(path1)
    to_label = tofile or str(path2)

    # Generate unified diff
    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile=from_label,
        tofile=to_label,
        lineterm='',
        n=context_lines
    )

    return '\n'.join(diff)
