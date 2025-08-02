import shutil
import subprocess
from typing import Any
from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass

from schema import Schema
from schema import Optional

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInputError
from spekulatio.exceptions import SpekulatioActionExecutionError
from ..action import Action


@dataclass
class Run(Action):

    def validate_parameters(self):
        """Check that the provided parameters match what the action expects."""
        schema = Schema(
            {
                "command": str,
                Optional("shell", default=True): bool,
                Optional("timeout", default=None): int,
            }
        )
        schema.validate(self.parameters)

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Execute a command."""

        # get command
        raw_command = self.parameters["command"]
        command_template = env.from_string(raw_command)
        values["_output_path"] = output_path
        command = command_template.render(values)
        log.debug(f"Run - command: '{command}'")

        # execute it
        shell = self.parameters.get("shell", True)
        timeout = self.parameters.get("timeout", None)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                check=True,
                text=True,
                shell=shell,
                timeout=timeout,
            )
        except subprocess.CalledProcessError as e:
            raise SpekulatioActionExecutionError(
                f"Run action a non-zero return code: {e.returncode}\n"
                f"Command: {command}\n"
                f"stderr: {e.stderr}"
            )
        except subprocess.TimeoutExpired:
            raise SpekulatioActionExecutionError(
                f"Run action reached timeout: {timeout}s\n" f"Command: {command}"
            )
        else:
            log.debug(f"Run - return code: {result.returncode}")
            log.debug(f"Run - stdout: '{result.stdout}'")
            log.debug(f"Run - stderr: '{result.stderr}'")

        # check that the file was generated
        if self.generates_output:
            if not output_path.exists():
                raise SpekulatioActionExecutionError(
                    f"Run action a didn't generate an output file:\n"
                    f"Command: {command}\n"
                    f"Expected file: {output_path}\n"
                    "Note: set 'generates_output: false' in the action definition to skip this check."
                )
