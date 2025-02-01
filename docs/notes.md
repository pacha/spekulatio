
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

* `input_path`: input directory provided by the user using the Spekulatio `build` command.
* `spekulatio_path`: path to one Spekulatio recipe file (ie. `spekulatio.yaml` file).
* `recipe_path`: path specified in a Spekulatio recipe file.
* `layer_path`: is the actual path used by the recipe. It is equal to `input_path` in the
  case of `user-files` recipes, and equal to `recipe_path` in the case of `recipe-files` recipes.
* `output_path`: path where the final output is written.

