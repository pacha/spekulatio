# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spekulatio is a command-line tool that transforms directories based on rules defined in `spekulatio.yaml` files. It can be used for rendering YAML manifests, bootstrapping project directories, or as a static site generator.

## Development Commands

### Setup
```bash
just setup                    # Install development dependencies
```

### Testing
```bash
just test-all                 # Run all tests
just test <path>              # Run specific test with verbose output
just test tests/test_*.py     # Run specific test file
```

### Code Quality
```bash
just lint                     # Check code with ruff
just fix                      # Auto-fix ruff issues
just format                   # Format code with ruff
just check-pyright            # Type check with pyright
just check-mypy               # Type check with mypy
```

## Architecture

### Core Models
- **Recipe** (`spekulatio/models/recipe.py`): Represents a `spekulatio.yaml` configuration file
- **Layer** (`spekulatio/models/layer.py`): Manages layered configurations that merge together
- **Node** (`spekulatio/models/node.py`): Represents files/directories in the input tree
- **Action** (`spekulatio/models/action.py`): Base class for transformations applied to nodes

### Built-in Actions
Located in `spekulatio/models/actions/`:
- `Copy`: Copy files without transformation
- `Render`: Render files using Jinja2 templates
- `Md2Html`: Convert Markdown to HTML
- `RenderJson`/`RenderYaml`: Render JSON/YAML data into templates
- `Unzip`: Extract zip files

### Operations Flow
1. **get_recipes**: Parse `spekulatio.yaml` files and merge layers
2. **create_tree**: Build node tree from input directories
3. **write_tree**: Apply actions and write output files

### Commands
- `spekulatio build`: Main command to transform directories
- `spekulatio show`: Display configuration and node trees
- `spekulatio serve`: Development server with live reload

### Key Directories
- `spekulatio/commands/`: CLI command implementations
- `spekulatio/operations/`: Core processing logic
- `spekulatio/lib/`: Utility functions (frontmatter parsing, values parsing)
- `tests/_fixtures/`: Test data for various scenarios
- `tests/_projects/`: Integration test projects with input/output examples

### Configuration System
Spekulatio uses YAML configuration files with support for:
- Layered configurations that merge together
- Value inheritance through directory hierarchies
- Pattern matching for applying actions to files
- Custom action parameters and output naming