
from typing import Any
from pathlib import Path
from dataclasses import field
from dataclasses import dataclass

import markdown
from schema import Schema
from schema import Optional

from spekulatio.exceptions import SpekulatioValidationError
from ..action import Action

@dataclass
class Md2Html(Action):
    patterns: tuple[str] = ("*.md", "*.mkd", "*.mkdn", "*.mdwn", "*.mdwon", "*.markdown")
    output_name_template: str = "{{ _this.input_path.with_suffix('.html').name }}"
    frontmatter: bool = True

    # def validate_parameters(self):
    #     """Check that the provided parameters match what the action expects."""
    #     try:
    #         schema = Schema(
    #             {
    #                 Optional("render_content", default=True): bool,
    #                 Optional("extensions", default=[]): list[str],
    #                 Optional("extension_configs", default={}): {str: dict},
    #                 Optional("output_format", default="html5"): str,
    #                 Optional("tab_length", default=4): int,
    #             }
    #         )
    #         _ = schema.validate(self.parameters)
    #     except Exception as err:
    #         raise SpekulatioValidationError(
    #             f"Wrong parameters for Md2Html action: {err}"
    #         )

    # def get_values(self, input_path: Path) -> dict[Any, Any]:
    #     """Return values provided by the user in the front-matter."""

    #     # skip if frontmatter shouldn't be detected
    #     if not self.parameters['extract_frontmatter']:
    #         return {}

    #     # extract frontmatter
    #     text = input_path.read_text()
    #     src, frontmatter_values = extract_frontmatter(text)

    #     # create values to return
    #     values = {}
    #     values["_src"] = src
    #     values.update(frontmatter_values)

    #     return values

    # def get_values(self, input_path: Path, output_path: Path, values: dict[Any, Any]) -> dict[Any, Any]:
    #     """Return values generated by the Action."""

    #     # get body
    #     src = values["_src"]
    #     if self.parameters['render_content']:
    #         body = render_text(src, values)
    #     else:
    #         body = src

    #     # convert
    #     md = markdown.Markdown(
    #         extensions=self.parameters['extensions'],
    #         extension_configs=self.parameters['extension_configs'],
    #         output_format=self.parameters['output_format'],
    #         tab_length=self.parameters['tab_length'],
    #     )
    #     content = md.convert(body)

    #     action_output = {
    #         "toc": md.toc_tokens,
    #     }

    #     extra_values = {
    #         "_toc": toc,
    #         "_content": content,
    #     }

    # def execute(self, input_path: Path, output_path: Path, values: dict[Any, Any]):
    #     """lkj."""