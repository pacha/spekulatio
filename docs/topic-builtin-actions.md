
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

* `extensions`: (List of strings) Markdown extensions to enable. See entire list
  of supported extensions at [Python Markdown
  Extensions](https://python-markdown.github.io/extensions/).
