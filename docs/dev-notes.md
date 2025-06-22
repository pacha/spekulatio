
# Dev notes

## Spekulatio recipes

Spekulatio transforms directories following a number of actions over an input
directory. Those actions are specified in a "recipe file" typically named
`spekulatio.yaml`.

A Spekulatio recipe file has three parts (all optional):

* Layers: this defines links to other recipe files that have to be processed
  before this one.
* Main block: this specifies the layer that is created by this recipe file. The
  two most important parts of a main block definition are the `path` and the
  list of `actions`.
* Values: the values defined by this recipe and that affect to all layers (both
  the ones specified in `layers` and the one of the main block).

## Recipe modes

There are three kinds of Spekulatio recipes:

* `user-files` recipes: Recipes that just apply transformations to the
  directory provided by the user. An example of this is a recipe that renders
  all the YAML files in a given directory. these recipes are constituted by a
  single recipe file (eg. `spekulatio.yaml`). The input directory is passed as
  a parameter to Spekulatio's `build` command. 
* `recipe-files` recipes: Recipes that generate the files that end up in the
  output directory by themselves. An example of this is a "cookie cutter"
  recipe that generates the basic file structure of a new project in a
  programming language. These recipes don't need an input directory provided by
  the user.
* `no-files` recipes: Recipes that don't generate any files in the output by
  themselves, but that aggregate layers created by other recipes by listing
  them in the `layers` section of the recipe file.

## Path names

* `input_path`: input directory provided by the user using the Spekulatio
  `build` command. Recipes can define their own `input_path` in the Spekulatio file. When that happens,
  the input path of the recipe is used instead of the one provided by the user. Recipes that don't have
  their own `input_path` defined use the one of the user though, independently of them being nested
  as layers of a main recipe.
* `spekulatio_file_path`: path to one Spekulatio recipe file (eg. `spekulatio.yaml` file).
* `recipe_path`: path passed by the user pointing to either a recipe directory or a Spekulatio file.
  A recipe path must be passed to the `build` command as the first parameter. Each layer
  defined in a Spekulatio file must also provide a recipe path.
* `output_path`: directory where the output is generated.

Example 1:
```
recipes/
    foobar/
        spekulatio.yaml (with no `path` attribute)
input-dir/
    index.md
output-dir/
    index.html

$ spekulatio build recipes/foobar -i input-dir -o output-dir

input_path: input-dir/
recipe_path: recipes/foobar
spekulatio_file_path: recipes/foobar/spekulatio.yaml
output_path: output-dir/
```

Example 2:
```
recipes/
    foobar/
        spekulatio.yaml (with `path: .`)
        README.md
        some-file.yaml
output-dir/
    README.md
    some-file.yaml

$ spekulatio build recipes/foobar -o output-dir

input_path: recipes/foobar/
recipe_path: recipes/foobar
spekulatio_file_path: recipes/foobar/spekulatio.yaml
output_path: output-dir/
```

