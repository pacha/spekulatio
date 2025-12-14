"""Git repository cache management."""

import re
from pathlib import Path

try:
    from platformdirs import user_cache_dir
except ImportError:
    # Fallback for systems without platformdirs
    import os
    def user_cache_dir() -> str:
        if os.name == 'nt':  # Windows
            return os.path.expandvars(r'%LOCALAPPDATA%')
        elif os.name == 'posix':
            if 'darwin' in os.uname().sysname.lower():  # macOS
                return os.path.expanduser('~/Library/Caches')
            else:  # Linux and other Unix-like
                return os.path.expanduser('~/.cache')
        else:
            return os.path.expanduser('~/.cache')


def get_cache_dir() -> Path:
    """Get the platform-specific cache directory for Spekulatio Git repositories.
    
    Returns:
        Path to the Git cache directory
    """
    cache_root = Path(user_cache_dir())
    return cache_root / "spekulatio" / "git"


def uri_to_safe_dirname(uri: str) -> str:
    """Convert a Git URI to a filesystem-safe directory name.
    
    Replaces problematic characters while preserving domain structure.
    
    Args:
        uri: Git URI like "https://github.com/user/repo.git@branch"
        
    Returns:
        Safe directory name like "github.com_user_repo_branch"
    """
    # Remove protocol
    clean_uri = re.sub(r'^https?://', '', uri)
    clean_uri = re.sub(r'^git@', '', clean_uri)
    
    # Remove .git suffix before character replacement (may not be at end due to @ref)
    clean_uri = re.sub(r'\.git(?=@|$)', '', clean_uri)
    
    # Replace problematic characters
    replacements = {
        '/': '_',
        ':': '_',
        '@': '_',
        '?': '_',
        '#': '_',
        '&': '_',
        '=': '_',
        ' ': '_',
    }
    
    for char, replacement in replacements.items():
        clean_uri = clean_uri.replace(char, replacement)
    
    # Remove multiple consecutive underscores
    clean_uri = re.sub(r'_+', '_', clean_uri)
    
    # Remove leading/trailing underscores
    clean_uri = clean_uri.strip('_')
    
    return clean_uri


def get_repo_cache_path(uri: str) -> Path:
    """Get the cache path for a specific Git URI.
    
    Args:
        uri: Git URI
        
    Returns:
        Path where the repository should be cached
    """
    safe_name = uri_to_safe_dirname(uri)
    return get_cache_dir() / safe_name


def is_repo_cached(uri: str) -> bool:
    """Check if a repository is already cached.
    
    Args:
        uri: Git URI
        
    Returns:
        True if repository exists in cache
    """
    cache_path = get_repo_cache_path(uri)
    return cache_path.exists() and cache_path.is_dir() and (cache_path / ".git").exists()