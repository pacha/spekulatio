
# Reference

## spekulatio.yaml file

Example displaying all fields:

    layers:
      - path: /path/to/some/other/spekulatio.yaml
    path: .
    values_file: "_values.yaml"
    actions:
      - name: Md2Html
        package: spekulatio
        patterns:
        - "*.md"
        - "*.markdown"
        output_name: "{{ _input_name.with_suffix('.html') }}"
        parameters:
          extensions:
            - toc
            - fenced_code
    values:
      foo: 1

### `layers` (List | Optional | Default: [])

This is a list of `spekulatio.yaml` files that should be processed before the
current one (_the parent_). The result of processing all layers is merged
together into a single output directory. The list is processed in order, with
later entries overriding the result of the previous ones for output files with
the same path. The processing of the parent Spekulatio file has higher priority
than any of the layers (exactly as if it were the last layer applied).

A `spekulatio.yaml` file can be composed of a single `layers` entry with the
list of child Spekulatio files to process. It is not mandatory to have a
`rules` entry.

For each layer:

* `path` (String | Required): location of the child `spekulatio.yaml` file.
* `values` (Dictionary | Optional | Default: {}): dictionary of values to pass
  to the first node of the layer (see [LINK:working-with-values]). If the
  `spekulatio.yaml` file pointed by `path` defines `default_values`, the values in
  this dictionary will override the default ones.

### `path` (String | Optional | Default: `.`)

Path to the input dictionary to process.

### `preset` (String | Optional | Default: None)

Name of the preset to use. A preset is a reusable list of rules (see
[LINK:presets]). The rules in the preset have less precedence than the rules
listed in the `rules` key.

### `rules` (List | Optional | Default: [])

List of rules to transform the input directory located at `path` into the final
output directory.

For each entry in the rules list:

* `name` (String | Required): name of the rule to apply (eg. `Copy`,
  `MD2HTML`, …).
* `package` (String | Optional | Default: `spekulatio`): name of the Python
  package which the rule can be imported from. All rules in Spekulatio
  are Python classes. The `name` of the rule is the name of the class and
  Spekulatio imports the rule using something equivalent to `from
  <package> import <name>`. `package` is `spekulatio` by default, which
  means that you don't have to specify anything if you're just using
  Spekulatio built-in rules. If you want to define your own, though, you
  can use `package` to indicate the tool where to find your rules (see
  [LINK:custom-rules]).
* `patterns` (List | Required): list of patterns in wildmatch format (see
  [LINK:wildmatch]). Files matching any of these patterns will be transformed
  using this rule.
* `output_filename` (String | Optional | Default: <determined by the rule>):
  Jinja template string that determines the format of the output filename
  generated by the application of the rule. Typically, there's no need to pass the output
  filename format as each action defines their own. For example, the
  built-in Markdown to HTML rule (`MD2HTML`) will check for input
  filenames ending in `.md`, `.markdown`, … and so on, and define the output
  filename as `{{ input_path.with_suffix('.html').name }}`, which means:
  "take the input path, replace the file extension by `.html`, and remove the
  directory part of the path leaving only the filename itself". The
  `output_filename` template should always generate a filename without
  directories.
* `parameters` (Dictionary | Optional | Default: {}): parameters that will
  be passed when the rule is applied. Check the documentation of the
  particular rule you're using to see which ones are available.
  The keys of the parameters dictionary are always strings, the values must
  be of the type specified in the documentation of the rule.

#### Jinja template variables in rules

[TODO]

### `values` (Dictionary | Optional | Default: {})

Dictionary of values to pass to the first node of the generated output tree.
(see [LINK:working-with-values]).

### `default_values` (Dictionary | Optional | Default: {})

This is similar to `values`. However, if this `spekulatio.yaml` file is linked
from the `layers` section of a parent Spekulatio file, the values passed from
there will override this default values.

For example:

    # parent spekulatio.yaml file
    layers:
      path: /some/child/spekulatio.yaml
      values:
        fg_color: green

    # /some/child/spekulatio.yaml
    default_values:
      fg_color: red
      bg_color: blue

Here, the final value of `fg_color` will be `green` as the default value will be
overridden by the value set in the parent file. However, `bg_color` will be
`blue` as the value is not overridden and the default one will be used.

## Node Object

When rendering templates, you can inspect the tree that represents the
output directory that will be created. Each node of the tree has the following
attributes:

`node.input_path`

Relative path of the input file associated to the node (from the location of the
`spekulatio.yaml` file).

`node.output_path`

Relative path of the output file associated to the node (from the root of, but
not including, the output directory).

`node.action`

Name of the action to apply to the input file.

`node.values`

Dictionary of values for that node (it includes all the values that are
inherited or defined in that node).

`node.parent`

Reference to the node's parent.

`node.children`

Sorted list of children nodes.

`node.prev`

Reference to the previous node (in pre-order traversal)

`node.next`

Reference to the next node (in pre-order traversal)

## Read Values

These are values that are available during the rendering of templates:

`_this` (Node)

Node that correspond to the file being rendered.

`_root` (Node)

Root node of the output tree.

## Write Values

`_sort` (list | default: ["*"])

Sort the children elements of a directory. This sorting affects the order in
which templates will get the nodes when inspecting the children of a directory
node.

For example for a directory like this one:
```
some-dir
├── a.txt
├── b.txt
├── c.txt
├── dir1/
├── dir2/
└── _values.yaml
```
You can reorder the files and directories by just listing their names:
```
# _values.yaml
_sort:
  - c.txt
  - dir1
  - b.txt
  - "*"
  - dir2
```
Note that:

* You can only sort _immediate_ children of the current directory. Using
  something like `foo/bar.txt` results in an error.
* You can use the special entry `"*"` to place all the files that are not listed
  explicitly. If not specified, all non-listed files/directories are placed at
  the end in alphabetical order.
* By default, the sorting value is `"*"` which results in the files/directories
  being sorted alphabetically.

`_output_name` (jinja template)

Variable used to override the output name template set in the `spekulatio.yaml`.
If placed inside a front-matter, the corresponding output file is renamed
accordingly. If placed inside a `_values.yaml` file, it is the output directory
associated to the containing directory the one named according to the template
provided.

