
# Built-in Actions

## Md2Html

Converts Markdown files to HTML5.

_Default rule attributes_

* `package`: `spekulatio`
* `patterns`:
    * `*.md`
    * `*.mkd`
    * `*.mkdn`
    * `*.mdwn`
    * `*.mdwon`
    * `*.markdown`
* `output_name`: `"{{ _this.input_path.with_suffix('.html').name }}"`

_Provided values_

* `title`: (String) Top level title of the document. Empty string if not present.
* `toc`: (Nested list of strings) Table of contents of the document.
* `src`: (String) Original Markdown content.

_Parameters_

* `render_content` [boolean | default: `true`]: if set to `true`, the
  Markdown content will be rendered using the values passed to the action. This
  allows to use Jinja constructs inside the Markdown body itself. If set to
  `false`, the Markdown content is taken verbatim.
* `extract_frontmatter` [boolean | default: `true`]: Md2Html always checks if
  there's a frontmatter at the top of the Markdown file. If there's one, the
  values defined there are added to the values passed to the action. If there's
  no frontmatter, no action is taken. This parameter only has to be changed if
  the frontmatter detection is undesirable for any reason. It is safe to leave
  it set to `true` even for files without frontmatter.
* `extensions`: (List of strings) Markdown extensions to enable. See entire list
  of supported extensions at [Python Markdown
  Extensions](https://python-markdown.github.io/extensions/).
