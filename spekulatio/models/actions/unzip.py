
import zipfile
from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log

from ..action import Action

@dataclass
class Unzip(Action):
    patterns: tuple[str] = ("*.zip", "*.ZIP")
    output_name: Optional[str] = "{{ _input_name.stem }}"

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Unzip file.

        If the input path is /.../baz.zip, the files will be extracted to /.../baz/
        """
        # create directory
        output_path.mkdir(exist_ok=True)

        # unzip file
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
