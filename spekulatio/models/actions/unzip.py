import zipfile
from typing import Any
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError

from ..action import Action


@dataclass
class Unzip(Action):
    patterns: tuple[str] = ("*.zip", "*.ZIP")
    output_name: Optional[str] = "{{ _input_path.stem }}"

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Unzip file.

        If the input path is .../baz.zip, the files will be extracted to .../baz/
        """
        # create directory
        output_path.mkdir(exist_ok=True)

        # unzip file with path validation to prevent zip slip attacks
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            resolved_output_path = output_path.resolve()

            # validate all paths before extraction
            for member in zip_ref.infolist():
                # resolve the path to check for directory traversal
                member_path = Path(member.filename)
                target_path = (output_path / member_path).resolve()

                # ensure the target path is within the output directory using pathlib
                try:
                    target_path.relative_to(resolved_output_path)
                except ValueError:
                    # relative_to() raises ValueError if target_path is not under resolved_output_path
                    raise SpekulatioInputError(
                        f"Unsafe path in zip file: '{member.filename}' would extract to '{target_path}' "
                        f"which is outside the target directory '{resolved_output_path}'"
                    )

            # if all paths are safe, extract
            zip_ref.extractall(output_path)
