from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from spekulatio.logs import log
from spekulatio.lib.jinja_extra import get_extra_globals
from spekulatio.models import Node
from spekulatio.paths import default_template_path


def write_tree(output_path: Path, root: Node, cache: bool) -> None:
    """Generate the output file structure from an in-memory tree."""

    # get Jinja environment
    default_dirs = [str(default_template_path)]
    recipe_dirs = [str(layer.path) for layer in root.layers]
    template_dirs = list(reversed(default_dirs + recipe_dirs))
    env = Environment(loader=FileSystemLoader(template_dirs))
    env.globals.update(get_extra_globals())

    # write nodes
    for node in root.traverse(unsorted=True):
        node.write(base_output_path=output_path, cache=cache, env=env)
