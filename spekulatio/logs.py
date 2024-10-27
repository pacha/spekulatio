
import pprint
import logging
import textwrap
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

log = logging.getLogger("spekulatio")
log.addHandler(logging.NullHandler())

def configure_logging(level):
    error_console = Console(stderr=True)
    logging.basicConfig(
        level="WARN",
        format="%(message)s",
        handlers=[RichHandler(console=error_console, show_time=False, show_path=False)],
    )
    log.setLevel(level)

def log_obj(level: str, message: str, obj_retriever: Any, indent=0):
    """Log a complex object, pretty printed and without affecting performance.

    * Instead of passing an object, which requires computing it even if the log
      doesn't have to be emitted due to the log level -and therefore making the
      code unnecessarily less efficient-, the `obj_retriever` function is passed,
      which will be called to generate the object only if the current log level
      requires emitting this log.
    * The message is emitted as-is separated from a new line from the
      pretty-formatted object representation.
    """
    # get correct level
    level = level if isinstance(level, int) else logging.getLevelName(level)

    # log only for the correct log level
    if log.isEnabledFor(level):
        obj = obj_retriever()
        obj_message = pprint.pformat(obj)
        obj_message = textwrap.indent(obj_message, indent * ' ')
        full_message = f"{message}\n{obj_message}"
        log.log(level, full_message)
