
from typing import ClassVar
from pathlib import Path
from dataclasses import dataclass

from .create_dir import CreateDir


@dataclass
class RenameDir(CreateDir):
    once_per_branch: ClassVar[bool] = True

    def match(self, root_path: Path, relative_path: Path) -> bool:
        absolute_path = root_path / relative_path
        # only match directories
        if not absolute_path.is_dir():
            return False
        is_a_match = self.parser.match(relative_path)
        return is_a_match
