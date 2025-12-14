
CONTEXT:

When a user uses this tool (`spekulatio build`), they can specify the transformations to perform to the files of an input directory to create the final result in output directory.

Those transformations are specified in a "recipe". A recipe consists of a `spekulatio.yaml` file and an optional set of files and directories, referred to as the `input_path`. If a recipe provides its own input_path, then the transformations (actions) listed in `spekulatio.yaml` are performed on it. If it doesn't, then the transformations are performed in the input path provided by the user.

You can see examples of recipes in the `tests/_projects` directory or the repository.

A recipe can include other recipes. To specify a recipe for the `spekulatio build` command (or as a nested recipe), it is necessary to just pass a directory that contains a `spekulatio.yaml` file.

TASK:

I would like the application to allow users to provide Git URIs in addition to directories to specify recipes.
That way, one can easily share recipes with other users by just having them stored in a service like GitHub.

Please, make the necessary changes to the code, such that:

* The `build` command can take a Git URI or a directory to specify the recipe to use
* When a Git URI is used, then the program will first clone the repository into a "cache" directory (eg. typically `.cache` in Linux systems, but the solution has to be valid cross-platform for Linux, MacOS and Windows).
* Once the repository is cloned, the `input_path` will be pointed to it and the Recipe model will work as it is right now without modification, as it won't behave differently if the input directory was already in the local system of first cloned.
* To avoid cloning repositories on each execution, if the repository is already in the cache directory, it will be reused. It is necessary that the latest version of the code is used, which means that it has to be pulled first before executing the transformation actions.
* The user should be able to specify which branch of the repository to use, and that branch should be the one checked out after the clone. Ideally, the branch is specified in the URI.
* Inside the cache directory, each repository should be stored inside a root directory named `spekulatio` and then inside a directory named using the URI provided, but ensuring that the name only has valid characters for Linux, MacOS and Windows file systems. There has to be a 1:1 relationship between the URI itself and its safe representation as a directory. Having each URI linked to a directory prevents clashes between different repositories with the same name in the cache directory (for example, if they have the same name but come from different Git servers). Since the repository branch is to be specified in the URI, it is possible that the same repository is cloned multiple times (once per branch). That is ok, as it requires more space but also allow the parallel execution of Spekulatio builds without conflicts arising from switching branches in the middle of a run.
* If there's a safe way to do a "shallow" clone of a branch without having to download its entire history, then that's how the clone should be made (the code to be used will be always the latest inside the branch).
* The only requirement for this new feature to work is that the Git commands are available in the local system. If the `git` command tool is not available, a user friendly error message should be displayed to the user (using the `log.error(...)` mechanism already present across the project).
* In addition to the `build` command taking an URI, it is necessary that the `layers` section in the `spekulatio.yaml` directory also allows URIs to be used there, so that nested recipes can also be retrieved from git repositories. The mechanism of caching these repositories is identical to the one described for the `build` command.
* All the code necessary to execute Git commands (and independent from the application business logic) should go into a `spekulatio/lib/git` directory.
* You can use the Python external dependency `platformdirs` to ensure that a suitable folder for the `.cache` directory is selected.
* Whenever a Git clone (or pull) happens, the user should be notified with an INFO message in the logging system.
