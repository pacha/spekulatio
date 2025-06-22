
project_dir := justfile_directory()

@help:
  just --list

@setup:
  uv pip install ".[dev]"

@test-all:
  uv run python -m pytest --capture=no -o log_cli=false tests/

@test *params:
  uv run python -m pytest -vv -x -o log_cli=true {{ params }}

@lint:
  uv run ruff check

@fix:
  uv run ruff --fix

@format:
  uv run ruff-format

@check-pyright:
  uv run pyright

@check-mypy:
  uv run mypy
