"""Git operations for repository management."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from spekulatio.logs import log
from .uri import parse_git_uri
from .cache import get_repo_cache_path, is_repo_cached


def check_git_available() -> bool:
    """Check if git command is available.
    
    Returns:
        True if git is available in PATH
    """
    return shutil.which("git") is not None


def is_tag(repo_path: Path, ref: str) -> bool:
    """Check if a reference is a tag in the repository.
    
    Args:
        repo_path: Path to the Git repository
        ref: Reference name to check
        
    Returns:
        True if ref is a tag, False if it's a branch or doesn't exist
    """
    try:
        result = subprocess.run(
            ["git", "tag", "-l", ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0 and ref in result.stdout.strip().split('\n')
    except (subprocess.SubprocessError, OSError):
        return False


def clone_repository(uri: str, target_path: Path, ref: Optional[str] = None, ref_type: str = "branch") -> None:
    """Clone a Git repository.
    
    Args:
        uri: Git repository URI (without @ref suffix)
        target_path: Local path where to clone
        ref: Branch or tag name to checkout
        ref_type: Type of reference ("branch" or "tag")
        
    Raises:
        subprocess.CalledProcessError: If git command fails
        OSError: If git is not available
    """
    if not check_git_available():
        raise OSError("Git command not found. Please install Git and ensure it's in your PATH.")
    
    # Create parent directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build clone command
    cmd = ["git", "clone", "--depth", "1"]
    
    if ref:
        cmd.extend(["--branch", ref])
        if ref_type == "branch":
            cmd.append("--single-branch")
    
    cmd.extend([uri, str(target_path)])
    
    log.info(f"Cloning repository from {uri}...")
    if ref:
        log.info(f"Checking out {ref_type} '{ref}'...")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to clone repository {uri}"
        if e.stderr:
            error_msg += f": {e.stderr.strip()}"
        
        # Provide helpful error messages
        if "could not read Username" in e.stderr or "Authentication failed" in e.stderr:
            error_msg += "\nTip: Check your Git credentials or use a public repository."
        elif "Repository not found" in e.stderr:
            error_msg += "\nTip: Verify the repository URL and that you have access to it."
        elif "unable to access" in e.stderr:
            error_msg += "\nTip: Check your internet connection and firewall settings."
        
        log.error(error_msg)
        raise


def update_repository(repo_path: Path, ref_type: str) -> None:
    """Update a Git repository with the latest changes.
    
    Only updates branches, as tags are immutable.
    
    Args:
        repo_path: Path to the Git repository
        ref_type: Type of reference ("branch" or "tag")
        
    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    if ref_type == "tag":
        log.info(f"Using cached repository at {repo_path} (tags are immutable)")
        return
    
    if not check_git_available():
        raise OSError("Git command not found. Please install Git and ensure it's in your PATH.")
    
    log.info(f"Updating repository at {repo_path}...")
    
    try:
        # Pull latest changes
        subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to update repository at {repo_path}"
        if e.stderr:
            error_msg += f": {e.stderr.strip()}"
        
        log.error(error_msg)
        raise


def ensure_repository(uri: str) -> Path:
    """Ensure a Git repository is available locally.
    
    Clones the repository if not cached, or updates it if it exists.
    
    Args:
        uri: Git URI (with optional @ref suffix)
        
    Returns:
        Path to the local repository
        
    Raises:
        ValueError: If URI is invalid
        OSError: If git is not available
        subprocess.CalledProcessError: If git operations fail
    """
    if not check_git_available():
        log.error("Git command not found. Please install Git and ensure it's in your PATH.")
        raise OSError("Git command not found")
    
    # Parse URI to get repository URL and reference
    uri_info = parse_git_uri(uri)
    cache_path = get_repo_cache_path(uri)
    
    if is_repo_cached(uri):
        # Repository exists, update if it's a branch
        update_repository(cache_path, uri_info.ref_type)
    else:
        # Repository doesn't exist, clone it
        clone_repository(
            uri_info.repo_url,
            cache_path,
            uri_info.ref_value,
            uri_info.ref_type
        )
    
    return cache_path