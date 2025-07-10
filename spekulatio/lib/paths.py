import os
import logging
import shutil
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

def delete_directory_contents(dir_path: Path):
   """Deletes all files and subdirectories in the given directory without deleting the directory itself."""
   for item in dir_path.iterdir():
       if item.is_dir():
           shutil.rmtree(item)
       else:
           item.unlink()

def get_paths_from_env_var(env_var_name: str) -> list[Path]:
    """Get the list of paths defined in the 'env_var_name' environment variable."""
    spekulatio_path_str = os.environ.get(env_var_name, "")
    directories = spekulatio_path_str.split(os.pathsep)
    paths = []
    for directory in directories:
        if not directory:
            continue
        paths.append(Path(directory).expanduser().resolve())
    return paths

def search_project_in_path_list(project_marker: str, project_path: Path, root_paths: list[Path]) -> Path:
    """Looks if a project directory is present in the provided root path list.

    A "project" in this context is a path that contains a specific file or
    directory. For example, a Git repository can be differentiated by the
    existence of a ".git" directory inside it. In the same way, a Makefile file
    can describe the directory of a project that can be build with Make.

    project_marker: the file or directory that makes a directory a project of a
        specific kind (eg. .git, Makefile, Cargo.toml, ...)
    project_path: the relative path of the project we're looking for.
        The project marker can be already included or not in the path.
    path_list: list of absolute directories that may contain or not the project path.
    """
    if project_path.is_absolute():
        path = project_path / project_marker if not project_path.is_file() else project_path
        if path.is_file():
            return path.expanduser().resolve()
    else:
        for root_path in root_paths:
            path = root_path / project_path
            if not path.is_file():
                path = path / project_marker
            if path.is_file():
                return path.expanduser().resolve()
    msg = f"Can't find project at '{project_path}'. "
    if root_paths:
        msg += "Search directories: " + ", ".join([str(root_path) for root_path in root_paths])
    else:
        msg += "(No search directories provided)"
    raise ValueError(msg)
