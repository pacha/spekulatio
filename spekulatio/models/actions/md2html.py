from typing import Any
from pathlib import Path
from dataclasses import dataclass

import markdown
from schema import Schema
from schema import Optional
from jinja2 import Template

from spekulatio.exceptions import SpekulatioInternalError
from ..action import RenderFromTextAction


@dataclass
class Md2Html(RenderFromTextAction):
    patterns: tuple[str] = (
        "*.md",
        "*.mkd",
        "*.mkdn",
        "*.mdwn",
        "*.mdwon",
        "*.markdown",
    )
    output_name: str = "{{ _input_name.with_suffix('.html') }}"
    frontmatter: bool = True
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

    def execute(
        self, input_path: Path, output_path: Path, values: dict[Any, Any]
    ) -> None:
        """Render current file and write it to the output path."""

        # get source
        try:
            src = values["_src"]
        except KeyError:
            raise SpekulatioInternalError(
                f"Malformed action '{self.__class__.__name__}': '_src' must be defined "
                "before calling the execute method of this class."
            )

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
        values["_md"] = md
        values["_content"] = content
        if hasattr(md, "toc_tokens"):
            values["_toc"] = md.toc_tokens

        # get values
        env = values["_env"]
        template_name = values["_template"]

        # render template
        template = env.get_template(template_name)
        full_html_content = template.render(values)

        # write content
        output_path.write_text(full_html_content)
