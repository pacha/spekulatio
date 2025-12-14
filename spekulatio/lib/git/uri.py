"""Git URI parsing and validation."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitUriInfo:
    """Information parsed from a Git URI."""
    repo_url: str
    ref_type: str  # "branch" or "tag"
    ref_value: Optional[str]


def is_git_uri(path: str) -> bool:
    """Check if a path is a Git URI.
    
    Detects common Git URI patterns:
    - https://github.com/user/repo.git
    - git@github.com:user/repo.git
    - https://gitlab.com/user/repo
    """
    if not isinstance(path, str):
        return False
    
    # Check for common Git URI patterns
    git_patterns = [
        r'^https?://[^/]+/.+\.git(?:@.+)?$',  # https://host/path.git[@ref]
        r'^git@[^:]+:.+\.git(?:@.+)?$',       # git@host:path.git[@ref]
        r'^https?://github\.com/.+/.+(?:@.+)?$',  # GitHub without .git
        r'^https?://gitlab\.com/.+/.+(?:@.+)?$',  # GitLab without .git
    ]
    
    return any(re.match(pattern, path) for pattern in git_patterns)


def parse_git_uri(uri: str) -> GitUriInfo:
    """Parse a Git URI to extract repository URL and reference.
    
    Args:
        uri: Git URI like "https://github.com/user/repo.git@branch"
        
    Returns:
        GitUriInfo with parsed components
        
    Raises:
        ValueError: If URI is invalid
    """
    if not is_git_uri(uri):
        raise ValueError(f"Invalid Git URI: {uri}")
    
    # Split URI and reference
    if "@" in uri and uri.startswith("git@"):
        # Handle SSH URLs like git@github.com:user/repo.git[@ref]
        # Find the last @ after the first colon
        colon_pos = uri.find(":")
        if colon_pos == -1:
            # No colon found, malformed SSH URL
            repo_url = uri
            ref = None
        else:
            # Look for @ after the colon
            remaining = uri[colon_pos:]
            if "@" in remaining:
                # Split on the last @
                parts = uri.rsplit("@", 1)
                repo_url, ref = parts
            else:
                # No reference, just the SSH URL
                repo_url = uri
                ref = None
    elif "@" in uri:
        # Handle HTTPS URLs like https://github.com/user/repo.git@ref
        parts = uri.rsplit("@", 1)
        if len(parts) == 2:
            repo_url, ref = parts
        else:
            repo_url = uri
            ref = None
    else:
        repo_url = uri
        ref = None
    
    # Determine reference type
    ref_type = "branch"  # Default
    if ref:
        # Simple heuristic: if it starts with 'v' and contains dots, likely a tag
        if ref.startswith("v") and "." in ref:
            ref_type = "tag"
        # If it matches semantic versioning pattern, it's a tag
        elif re.match(r'^\d+\.\d+\.\d+', ref):
            ref_type = "tag"
    
    return GitUriInfo(
        repo_url=repo_url,
        ref_type=ref_type,
        ref_value=ref
    )