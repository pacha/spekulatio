from typing import Any
from pathlib import Path
from dataclasses import dataclass

import markdown
from schema import Schema
from schema import Optional
from jinja2 import Template

from spekulatio.logs import log
from spekulatio.exceptions import SpekulatioInternalError
from spekulatio.lib.parse_values import parse_values_from_frontmatter
from ..action import Action


@dataclass
class Md2Html(Action):
    patterns: tuple[str] = (
        "*.md",
        "*.mkd",
        "*.mkdn",
        "*.mdwn",
        "*.mdwon",
        "*.markdown",
    )
    output_name: str = "{{ _input_path.with_suffix('.html').name }}"
    render_content: bool = True

    def validate_parameters(self):
        """Check that the provided parameters match what the action expects."""
        schema = Schema(
            {
                Optional("extensions", default=[]): list[str],
                Optional("extension_configs", default={}): {str: dict},
                Optional("output_format", default="html5"): str,
                Optional("tab_length", default=4): int,
            }
        )
        schema.validate(self.parameters)

    def get_values(self, input_path: Path) -> dict[Any, Any]:
        """Parse frontmatter if present."""
        src, frontmatter_values = parse_values_from_frontmatter(input_path)
        values = {
            "_action": {
                "src": src,
            }
        }
        values.update(frontmatter_values)
        return values

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any], env
    ) -> None:
        """Render current file and write it to the output path."""

        # get source
        src = values["_action"]["src"]

        # get content
        if self.render_content:
            src_template = Template(src)
            md_content = src_template.render(values)
        else:
            md_content = src

        # convert markdown
        md = markdown.Markdown(**self.parameters)
        content = md.convert(md_content)

        # update values
        values["_content"] = content
        values["_action"]["md"] = md
        if hasattr(md, "toc_tokens"):
            values["_action"]["toc"] = md.toc_tokens

        # render template
        template_name = values["_template"]
        template = env.get_template(template_name)
        rendered_content = template.render(values)

        # write content
        output_path.write_text(rendered_content)
