
from typing import Any
from pathlib import Path
from dataclasses import dataclass

import sass

from ..action import RenderFromTextAction

@dataclass
class CompileSass(RenderFromTextAction):
    patterns: tuple[str] = ("[!_]*.sass", "[!_]*.scss", "[!_]*.SASS", "[!_]*.SCSS")
    output_name: str = "{{ _input_name.with_suffix('.css') }}"
    frontmatter: bool = False
    render_content: bool = False

    def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> None:
        """Render current file and write it to the output path."""

        # spekulatio specific importer
        def importer(name, src_path_str):
            """Import first from the values of the node, fallback to default behavior."""
            return [(name, values[name])] if name in values else None

        # list of importers (<priority>, <function>)
        importers = [(0, importer)]

        # get import paths (all layers in order)
        node = values["_this"]
        root = values["_root"]
        include_paths = [str(layer.path.resolve() / node.input_file_path.parent) for layer in root.layers]

        # get content
        content = sass.compile(
            filename=str(input_path), importers=importers, include_paths=include_paths, **self.parameters
        )

        # write file
        output_path.write_text(content)
