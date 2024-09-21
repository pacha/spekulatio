
# Tutorial

## Overview

Spekulatio is a tool used to generate an output directory from an input
directory by transforming the files of the input directory based on the rules
defined in a `spekulatio.yaml` file.

For example, if you have an input directory with Markdown and CSS files:
```
input-dir
├── file1.md
├── file2.css
└── spekulatio.yaml
```
You can generate the output directory by running:
```
$ spekulatio build -i /path/to/input-dir -o /path/to/output-dir
```
If we specify in our `spekulatio.yaml` file that we want to convert Markdown to
HTML and minimize the CSS files, then we'll generate an output directory like this:
```
output-dir
├── file1.html
└── file2-min.css
```
Spekulatio is agnostic about the purpose of the output directory. You can use it
to generate static websites, bootstrap your projects by using it as a
cookie-cutter tool or render Kubernetes manifests. It all depends on how you
compose the rules to apply.

## Rules

To specify which transformations must be applied to which files, you can use the
`rules` entry of the `spekulatio.yaml` configuration file. For example:
```
# spekulatio.yaml
rules:
  - action: Copy
    patterns:
      - "*.txt"
  - action: CompileSass
    patterns:
      - "*.sass"
      - "*.scss"
```
The files of the input directory are matched against the patterns of each rule
in the order they are listed. When there's a match, the action of the rule is
executed. In the example above, text files are copied to the output directory
and SASS files (files with extension `.sass` or `.scss`) compiled into CSS
files.

Since the rules are checked in order, the rules at the beginning of the list
have priority over the ones at the end. If a file doesn't match any rule, then
no action is executed and that file won't generate a corresponding file in the
output directory.

### Patterns

Patterns must follow the _wildmatch_ syntax, which is the glob-like syntax used
in `.gitignore` files. One of the differences of wildmatch when compared to the
traditional glob syntax of the shell in terminals is that a pattern like `*.txt`
matches all text files with that extension recursively in the input directory.
To match files only at the root of the directory use `/*.txt`. Get a
more complete overview of the syntax here [LINK:wildmatch-syntax].

### Actions

There are a number of `actions` that are available in Spekulation by default.
One of the most interesting ones is `Run` with allows to run any arbitrary
command to transform the file:
```
rules:
  - action: Run
    patterns:
      - "*.png"
    params:
      command: "optipng {{ _input_path }} -out {{ _output_path }}"
```
The command parameter is a Jinja template that receives a number of
variables that you can use to compose the actual command to execute. Among other
variables, the template receives both the path to the input file (`_input_path`)
and the output one (`_output_path`). The leading underscore before a variable
means that it is provided by Spekulatio, as you can define your own ones too.

Other built-in actions available are:

* `Copy`: copy the file without modifying it.
* `Render`: use the input file as a Jinja template to render the output file.
* `RenderJson`: pass the contents of a JSON file to a template in order to
  render the output file.
* `RenderYaml`: pass the contents of a YAML file to a template in order to
  render the output file.
* `UseAsTemplate`: don't generate any output from this file, but use it as
  a Jinja template for other input files.
* `Md2Html`: convert a Markdown file to HTML.
* `CompileSass`: compile a SASS file (.sass or .scss) into CSS.

!!! Note

    **Custom Actions**

    You can also create your own actions/rules using Python. For more
    instructions on how to do that, take a look here [LINK:custom-rules].
    (Spoiler: you only need to create a class that has to fulfil some
    requirements and be available in the Python path).

### Output filename template

In a rule, you can also specify the name of the output file. For instance, in the
previous example:
```
rules:
  - action: Copy
    patterns:
      - "*.jpg"
      - "*.jpeg"
    output_filename: "{{ _input_name.with_suffix(".jpeg") }}"
```
In this case, all files with extensions `.jpg` and `.jpeg` are copied to the
output directory, but the final filename in each case is always normalized to
`.jpeg`.

### Parameters

There is another important field that can be used when defining a rule:
`parameters`. It allows you to control how the action will be executed. For
example, to enable the "fenced code" and "table of contents" extensions when
converting Markdown files to HTML, you can pass the `extensions` parameter:
```
rules:
  - action: Md2Html
    parameters:
      extensions:
        - toc
        - fenced_code
```

Each rule accepts a different set of parameters. To see which ones are accepted
by a specific rule check its documentation [LINK:built-in-rules].

### Default options

Finally, note that many times you can just define a rule by just listing an
action:
```
rules:
  - action: Md2Html
```
Each action defines its own default options. In this case, `patterns` will match
the most common extensions for Markdown (ie. `*.md`, `*.markdown`, `*.mdown`, …)
and will generate files with extension `*.html`. However, you can override these
default values by passing the fields explicitly.

## Values

We saw before that, when you use the `Run` action, you receive variables that
you can use in the `command` template like `_input_path` or `_output_path`:
```
rules:
  - action: Run
    patterns:
      - "*.png"
    params:
      command: "optipng {{ _input_path }} -out {{ _output_path }}"
```
However, Spekulatio allows you to create your own variables and also use them to
render files. To do so, you only have to place `_values.yaml` files at any
location in your input directory. For example, you could place this at the root
of the input directory:
```
# _values.yaml
project_name: "My Project"
author: "Serranito"
```
Note that the name of the variables can be chosen freely by you, the only
restriction is that the name can't start with an underscore, which is used by
built-in variable names provided by Spekulatio. The values can be of any type
allowed by the YAML syntax. That is, they can be string, numbers, dictionaries
or lists with any number of nested elements.

The variables defined in a `_values.yaml` file are available in the subdirectory
where the file is located and all its subdirectories. That means that if you
place the file at the root of the input dictionary, then its values will be
available all across the input directory.

Once, you have values defined, you can use them to render the contents of
plain-text files. For example, if you have this input directory:
```
my-project
├── README.md
├── _values.yaml
└── spekulatio.yaml
```

With the following contents:

`README.md`
```
# {{ project_name | upper }}

By {{ author }}.
```

`_values.yaml`
```
project_name: "My Project"
author: "Serranito"
```

`spekulatio.yaml`
```
rules:
  - action: Render
    patterns:
      - "*.md"
```

Then you'll obtain a `README.md` file as the only item in the output directory,
with the following unsurprising contents:
```
# My PROJECT

By Serranito.
```

### Operations with values

Once you place a `_values.yaml` file in a directory, all the files inside and
all the files in any descendant subdirectories have access to the variables
defined.

In the following example, `foo: 1` is accessible from all the files inside the
entire input directory (`file1`, `file2`, `file3`), while `bar: 2` is accessible
only by `file3`:
```
input-dir/
├── _values.yaml (foo: 1)
├── file1
├── dir1/
│   └── file2
└── dir2/
    ├── _values.yaml (bar: 2)
    └── dir4/
        └── file3
```

A `_values.yaml` file in a subdirectory can interact with the values that it
inherits. For example, it can just override a value:
```
input-dir/
├── _values.yaml (foo: 1)
├── file1
├── dir1/
│   └── file2
└── dir2/
    ├── _values.yaml (foo: 2)
    └── dir4/
        └── file3
```
Here:

* `file1` and `file2` see `foo: 1`
* `file3` sees `foo: 2`.

But also, it is possible to perform more complex operations such as
deleting a variable, appending elements to a list or merging dictionaries. To do
that, you need to use the syntax `key {operation}`, where `key` is the name of
the variable as defined in a `_values.yaml` file in a parent directory, and
`operation` is one of the available operations such as `set`, `delete`,
`rename`, `insert` or `extend`.
The following code shows, for example, how to add an element to a list:
```
# directory structure
foo/
├── _values.yaml
├── file1
└── dir2/
    ├── _values.yaml
    └── file2

# foo/_values.yaml
css_files:
- reset.css
- main.css

# foo/dir2/_values.yaml
css_files {insert}:
- theme2.css
```
The final value of `css_files` for `file1` is:
```
css_files:
- reset.css
- main.css
```
And for `file2` is:
```
css_files:
- reset.css
- main.css
- theme2.css
```
Check [LINK:value-operations] for more information about the available
operations and their syntax.

### Front Matter

As mentioned in the previous section, when you place a `_values.yaml` file in a
directory, all the files inside it and all the files in its subdirectories can
use those values. However, if you want to define values for a single file, you
can also do so using a _front matter_ which is a common way to add metadata to
the top of a plain text file as a YAML snippet:
```
---
project_name: "My Project"
author: "Serranito"
---

# {{ project_name }}

By {{ author }}.
```
The `Render` action, by default, detects if the input file has a front matter.
If the front matter is present, the variables are defined and the front matter
itself is removed from the output. If you want to prevent this behavior and the
front matter should be part of the output file, you can set the
`use_front_matter` parameter of the action to `false`:
```
rules:
  - action: Render
    patterns:
      - "*.md"
    parameters:
      use_front_matter: false
```

### Values in the spekulatio.yaml file

You can also define values directly in the `spekulatio.yaml` file:
```
rules:
  - action: Run
    patterns:
      - "*.png"
    params:
      command: "optipng -{{ level }} {{ _input_path }} -out {{ _output_path }}"
values:
  level: O7
```
Variables defined in this way are very similar to variables defined in a
`_values.yaml` file at the root of the input directory. The only difference is
that you can use the variables in the `rules` section of the configuration.

### Special values

In addition to your own defined values, Spekulatio passes to all Jinja templates
a number of built-in values. Built-in values always start with an underscore to
differentiate them from your own variables and avoid conflicts.

These are some of the most useful ones:

* `_foo`: 
* `_bar`: 
* ...

Note that some of them are just to be read, but others can also be set. When a
built-in variable is set it usually has a particular effect in the output of the
tool.

## Templates

The `Render` action is pretty simple, it just renders the content of the
matching files by passing the variables defined by the user and the built-in
ones to them. For cases in which multiple files must be rendered with the same
structure but with different content, you can use templates. These cases are
very common. For example, if you create a blog, probably most posts will share
the same HTML structure and only the content will vary from one to another. This
happens also if you want to generate a YAML manifest file that in which the
structure is the same and only some values change, for example, to adapt it to
production or development.

To define which files are used as templates use the `UseAsTemplate` action. Then
you can use `RenderJson` or `RenderYaml` to generate the output
files. Files marked as `UseAsTemplate` don't generate any output by themselves.

For example, the following input directory contains JSON files with
information about two retro computer games. Each JSON file is converted to a
HTML page about the game using the `game-page.html` template:
```
retro-games-input/
├── spekulatio.yaml
├── templates/
│   └── game-page.html
└── games/
    ├── tetris.json
    └── bubble-bobble.json
```
The output directory looks, then, like:
```
retro-games-output/
└── games/
    ├── tetris.html
    └── bubble-bobble.html
```
Note that the `templates/` directory is not included in the final result.
Spekulatio doesn't generate empty directories in the output. Since `templates/`
only contains a file that doesn't produce any output, the entire directory is
skipped. If you want to keep a empty directory in the output, just 
add an empty file named `.spekulatiokeep` in the input.

This is how the file contents could look like in the example above:
```
# spekulatio.yaml
rules:
  - action: UseAsTemplate
    patterns:
      - "templates/*.html"
  - action: RenderJson

# templates/game-page.html
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <ul>
            <li>publisher: {{ publisher }}</li>
            <li>year: {{ year }}</li>
            <li>genre:
                <ul>
                    {% for genre in genres %}
                    <li>{{ genre }}</li>
                    {% endfor %}
                </ul>
            </li>
        </ul>
    </body>
</html>

# games/tetris.json
{
    "_template": "templates/game-page.html",
    "title": "Tetris",
    "publisher": "Spectrum Holobyte",
    "year": "1988",
    "genres": ["Action", "Puzzle"]
}

# games/bubble-bobble.json
{
    "_template": "templates/game-page.html",
    "title": "Bubble Bobble",
    "publisher": "Taito",
    "year": "1986",
    "genres": ["Action", "Platforming"]
}
```
Some things to take into account:

* The fields defined in the JSON files are treated the same as the values
  defined in `_values.yaml`, and are directly accessible from the template.
* The special `_template` variable is used to tell Spekulatio which template
  should be used to render the output. In this example, probably all files in
  `games/` will use the same template, which means that it could make sense to add
  a `_values.yaml` file to that directory with this content: ``` _template:
  "templates/game-page.html" ``` so that the variable doesn't have to be added to
  each single JSON file.
* The `game-page.html` template uses Jinja syntax (like in any other case where
  text is rendered in Spekulatio), which offers `for` loops, `if` conditionals,
  dot notation for objects and many other structures that allow you to
  traverse complex nested structures.
* You can use YAML files instead of JSON ones by using the
  `RenderYaml` action instead of the `RenderJson` one with the same result as in
  this example. (In addition, you can also use TOML if you install the
  `spekulatio-extra` package.

### Rendering Markdown

While JSON and YAML are very convenient formats to pass metadata to a rendering
action, Markdown can be a more appropriate format for longer excerpts of text.
As we saw before, Spekulatio provides the `Md2Html` action to convert Markdown
into HTML.

For example, a `index.md` file like this:
```
---
_template: templates/index-page.html
---

# Retro Games!

Welcome to my page about videogames of old computer systems.
```
will be converted to HTML using the `templates/index-page.html` template and
saved in the output directory as `index.html`.

The `_template` variable is defined, in this case, in the [front matter]([LINK]),
which makes its value to apply only to this file.

When a Markdown file is processed by the `Md2Html` action, it is actually
internally converted to a dictionary with all the variables that are defined in
the front matter plus a special `_content` variable, that contains the Markdown
text already converted to HTML.

So, in the example above, the template receives these variables—in addition to
all the built-in ones passed by Spekulatio:
```
{
    "_template": templates/index-page.html,
    "_content": "<Markdown content converted to HTML>"
}
```

Since, the default values of the `Md2Html` action are to read all Markdown files
and convert them to HTML, the only entry in `rules` that we need inside the
`spekulatio.yaml` file is:
```
rules:
  - action: Md2Html
```

## Introspection

Let's put together the entire _Retro Games!_ website. We'll also add now a CSS file
to style our pages and we'll use the _introspection_ capabilities of Spekulatio
to create a list with links to the game pages in `games/`:

**Input directory**
```
input-retro-games/
├── spekulatio.yaml
├── static/
│   └── styles.css
├── templates/
│   ├── _values.yaml
│   ├── index-page.html
│   └── game-page.html
├── games/
│   ├── tetris.json
│   └── bubble-bobble.json
├── index.md
└── README.md
```

**Output directory**
```
output-retro-games/
├── static/
│   └── styles.css
├── games/
│   ├── tetris.html
│   └── bubble-bobble.html
└── index.html
```

`spekulatio.yaml`
```
rules:
  - action: Copy
    patterns:
      - "*.css"
  - action: UseAsTemplate
    patterns:
      - "templates/*.html"
  - action: RenderJson
  - action: Md2Html
      - "!README.md"
values:
  site_name: Retro Games!
  css_files:
    - static/styles.css
```

Which means:

* Copy any CSS file to the output directory using the same relative path.
* Use any HTML file in the `templates/` directory as templates (in this case,
  the provided pattern could drop the `templates/` directory and be just
  `"*.html"` since there are no other HTML files in the input directory).
* Render all JSON files in the input directory using templates.
* Render all Markdown files as HTML using templates, except for `README.md`,
  which should be skipped. (Since `README.md` is skipped in this rule and there
  are no other rules that match it, then it is ignored and not used to generate
  any output).
* The values defined here are inherited by the entire input directory.

`templates/index-page.html`
```
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">

        {% for css_file in css_files %}
            <link rel="stylesheet" href="{{ css_file }}">
        {% endfor %}

        <title>{{ site_name }}</title>
    </head>
    <body>
        {{ _content }}

        <h2>Game List</h2>
        <ul>
            {% for node in _get("/games").children %}
            <li>
                <a href="{{ node.url }}">{{ node.values.title }}</a>
            </li>
            {% endfor %}
        </ul>
    </body>
</html>
```

Here, `site_name` and `css_files` are variables defined in `spekulatio.yaml`.
And `_content` is the content of the Markdown file converted to HTML.

Before rendering any template, Spekulatio generates a tree with the contents of
the output directory. Each node of that tree is an output file. And then passes
special variables that allow you to inspect it from any template. In this case,
we're using that information to iterate through the files that will be generated
in the `games/` directory and we're generating a link to the resulting page.

The special variable `_root` can be used to access the root node of the output
tree. And to access a particular node inside the tree structure, you can use the
`_get` function. It takes as a parameter the path to the corresponding file in
the input directory. For example, if `input-directory/dir1/file.md` generates
`output-directory/dir1/file.html`, then you need to call `_get("/dir1/file.md")`
to get the `/dir1/file.html` node. If you use a leading slash (`/`) it means
that the path is relative to the input directory, if you omit it, then it means
that the path is relative to the directory that contains the file that is
currently being rendered. An example of this last case, if the file being
rendered is `/some/file.json` and in the template there's a call to
`_get("dir/file.md")`, then the retrieved node will be the corresponding to the
`/some/dir/file.html` file.

Nodes have a number of useful attributes:

* `node.children`: list of this node's children. It is an empty list for
  non-directory nodes.
* `node.url`: URL of the node if the output directory was being served. The
  `_url_prefix` variable can be used to append a specific prefix to each URL.
* `node.values`: dictionary with all the values defined and inherited by the
  node.

In the example above, we use this snippet to generate a list of links to the
game pages:
```
{% for node in _get("/games").children %}
<li>
    <a href="{{ node.url }}">{{ node.values.title }}</a>
</li>
{% endfor %}
```
Here, we can see that we're retrieving the directory node at `/games` and we
iterate through its children, which are the game pages, to generate
their links. For each page/node, we use the `url` and we access one of the
values defined in the JSON files (in this case the `title` of the game).

To see a complete list of attributes of a node, check [LINK: node reference].

In many occasions, you need to sort the children of a node in a specific order.
To learn how to do that, check the reference information of the `_sort` special
variable [LINK: `_sort` in special variables].

## Layers

So far we have seen the core concepts of Spekulatio: Rules, Values and
Templates. Knowing them is all you need to create websites, create project
templates or render manifests. However, there's one more concept that becomes
useful when you want to reuse Spekulatio projects: Layers.

For example, imagine that you want to create multiple sites that share the same
visual presentation, maybe just changing small details between them like the
color scheme or the font types. It would be useful in that situation to be able
to define a number of templates and static files (such as CSS and JavaScript
ones) and potentially some variables, that you could reuse between multiple
Spekulatio projects. _Layers_ allow you to do exactly that.

The _reusable_ part is defined exactly like any other Spekulatio project:
```
/path/to/reusable/theme/
├── spekulatio.yaml
├── static/
│   ├── script.js
│   └── styles.css
└── templates/
    ├── one-column.html
    └── two-columns.html

# spekulatio.yaml
rules:
  - action: Copy
    patterns:
      - "static/*.css"
      - "static/*.js"
  - action: UseAsTemplate
    patterns:
      - "templates/*.html"
values:
  primary_color: #F5A397
  secondary_color: #F5A397
```

Then, the _importing_ project can reference it in the `layers` section of its
`spekulatio.yaml` file:
```
/path/to/some/project/
├── spekulatio.yaml
├── section1/
│   ├── page1.md
│   └── page2.md
├── section2/
│   └── page3.md
└── index.md

layers:
  - path: /path/to/reusable/theme/spekulatio.yaml
rules:
  - action: Md2Html
values:
  secondary_color: #F5A397
```
By doing that, the `md` files can use the templates provided by the reusable
project and the static files get added to the output directory:
```
/path/to/output/
├── static/
│   ├── script.js
│   └── styles.css
├── section1/
│   ├── page1.html
│   └── page2.html
├── section2/
│   └── page3.html
└── index.html
```
Of course, the reusable theme can be referenced by multiple projects
simultaneously.

[TODO: explain referencing layers from specific git commits]

[TODO: explain variable inheritance with layers]

Layers are a quite flexible mechanism in Spekulatio. They don't have to
be used just to _add_ static files to the output. How layers work is that they
are just normal Spekulatio projects that are generated in the order
that they are listed:
```
layers:
  - path: /path/to/dir1/spekulatio.yaml
  - path: /path/to/dir2/spekulatio.yaml
  - path: /path/to/dir3/spekulatio.yaml
```
The final output directory is the combination of generating all the files for
each one. In fact, a `spekulatio.yaml` file that only lists layers like in the
example above is a perfectly valid Spekulatio configuration. If two layers
are supposed to generate a file in the same output path, then the layer listed
later "wins". That is, you can override files of the previous layers with files of
the next layers.

That means that you can have, for example, an entire project defined in the
first layer and then you can use layers to override some of the files. Or, as in
our first example, the first layer can generate only a few files and then the
main content can be in a different layer. How you organize your content into
layers is up to you. For example, you can have multiple teams generating
documentation for their own systems. You can then use layers to bring them
together under an unifying project, while each layer is still a independent
project on their own.

### Default Values

## Spekulatio Extra

As explained above, you can create your own custom actions to add to
Spekulatio's rules. They are only Python classes that must be available in the
`PYTHONPATH`. Spekulatio only defines a few core actions [LINK: action
reference]. But it offers an additional Python package `spekulatio-extra` that
provides some additional actions:

* `RenderToml`: like `RenderJson` and `RenderYaml` but for TOML files.
* `CompileSass`: compiles `.sass` and `.scss` files into `.css` files.
* `Rst2Html`: renders reStructuredText files (`.rst`) as HTML files (similar to
  how `Md2Html` works but for ReST files).

This package also includes a collection of templates that can be used to
generate websites quickly with Spekulatio.

To learn more check [LINK: spekulatio extra]

