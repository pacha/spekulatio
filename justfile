
project_dir := justfile_directory()

@help:
  just --list

@setup:
  pip install -e ".[dev]"

@test-all:
  pytest --capture=no -o log_cli=false tests/

@test *params:
  pytest -vv -x -o log_cli=true {{ params }}

@format:
  black {{ project_dir }}

@check:
  mypy {{ project_dir }}
