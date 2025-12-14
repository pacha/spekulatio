# Git Support Implementation Plan for Spekulatio

## Overview
This plan outlines the implementation of Git URI support in Spekulatio, allowing users to specify recipes using Git repositories instead of local directories.

## Architecture Design

### 1. Git URI Detection and Parsing
- **Location**: `spekulatio/lib/git/uri.py`
- **Purpose**: Parse and validate Git URIs with branch support
- **URI Formats**:
  ```
  https://github.com/user/repo.git
  https://github.com/user/repo.git@branch-name
  https://github.com/user/repo.git@v1.2.3
  git@github.com:user/repo.git
  git@github.com:user/repo.git@branch-name
  git@github.com:user/repo.git@v1.2.3
  ```
- **Functions**:
  - `is_git_uri(path: str) -> bool`: Check if path is a Git URI
  - `parse_git_uri(uri: str) -> GitUriInfo`: Extract repo URL and ref (branch/tag)
  - `GitUriInfo` dataclass with fields: `repo_url`, `ref_type` (branch/tag), `ref_value`

### 2. Cache Management
- **Location**: `spekulatio/lib/git/cache.py`
- **Purpose**: Manage cached Git repositories
- **Structure**:
  ```
  ~/.cache/spekulatio/
  └── git/
      ├── github.com_user_repo_main/
      ├── github.com_user_repo_feature-branch/
      ├── github.com_user_repo_v1.2.3/
      └── gitlab.com_org_project_develop/
  ```
- **Functions**:
  - `get_cache_dir() -> Path`: Get platform-specific cache directory using `platformdirs`
  - `uri_to_safe_dirname(uri: str) -> str`: Convert URI to filesystem-safe directory name
  - `get_repo_cache_path(uri: str) -> Path`: Get cache path for a specific URI (uses `uri_to_safe_dirname`)
  - `is_repo_cached(uri: str) -> bool`: Check if repository is already cached

### 3. Git Operations
- **Location**: `spekulatio/lib/git/operations.py`
- **Purpose**: Handle Git clone and pull operations
- **Functions**:
  - `check_git_available() -> bool`: Verify git command exists
  - `clone_repository(uri: str, target_path: Path, ref: Optional[str] = None, ref_type: str = "branch") -> None`: Clone with specific ref
  - `update_repository(repo_path: Path, ref_type: str) -> None`: Pull latest changes (only for branches)
  - `ensure_repository(uri: str) -> Path`: Main function that clones or updates as needed
  - `is_tag(repo_path: Path, ref: str) -> bool`: Check if ref is a tag or branch

### 4. Integration Points

#### A. Recipe Resolution Enhancement
- **File**: `spekulatio/operations/get_recipes.py`
- **Changes**:
  - Add new function `resolve_recipe_location(location: str) -> Path`:
    - Check if location is a Git URI using `is_git_uri()`
    - If Git URI: call `ensure_repository()` to get local cached path (absolute)
    - If local path: convert to Path and return
    - This function is called BEFORE `search_project_in_path_list()`
  - `search_project_in_path_list()` remains unchanged - only handles local directories
  - Update `get_recipes()` to accept `recipe_location: str` parameter instead of `recipe_path: Path`
  - Modify the recipe loading flow to first resolve Git URIs to local paths

#### B. Build Command
- **File**: `spekulatio/commands/build.py`
- **Changes**:
  - Rename CLI argument from `recipe` to `recipe_location` (line 19)
  - Keep `recipe_location` parameter as string instead of converting to Path immediately
  - Pass recipe location string to `build_operation()`
  - Update `build_operation()` call to pass `recipe_location` instead of `recipe_path`

#### C. Build Operation
- **File**: `spekulatio/operations/build.py`
- **Changes**:
  - Update `build()` function signature to accept `recipe_location: str` instead of `recipe_path: Path`
  - Pass recipe location string to `get_recipes()`

#### D. Layer Processing
- **File**: `spekulatio/operations/get_recipes.py` (in `_get_recipe_with_layers()`)
- **Changes**:
  - When processing layer paths, use `resolve_recipe_location()` before calling `search_project_in_path_list()`
  - Apply same Git resolution logic as main recipe

#### E. Show Commands
- **Files**: `spekulatio/commands/show/recipes.py`, `show/tree.py`, `show/layers.py`
- **Changes**:
  - Rename CLI argument from `recipe` to `recipe_location`
  - Keep consistent naming with build command
  - Pass location as string until resolution

## Implementation Steps

### Phase 1: Git Library Foundation
1. Create `spekulatio/lib/git/` directory structure
2. Implement URI parsing and validation
3. Implement cache directory management with platformdirs
4. Implement Git operations with error handling

### Phase 2: Core Integration
1. Modify recipe resolution to detect and handle Git URIs
2. Update all recipe path parameters to use consistent naming:
   - CLI arguments: `recipe` → `recipe_location`
   - Function parameters accepting strings: `recipe_location: str`
   - Function parameters accepting paths: `recipe_path: Path`
   - Recipe objects: `recipe: Recipe` or `recipes: list[Recipe]`
3. Add logging for Git operations (clone/pull)
4. Ensure proper error handling for missing Git

### Phase 3: Testing and Polish
1. Add unit tests for Git library components
2. Add integration tests with mock Git repositories
3. Update documentation

## Key Implementation Details

### Naming Conventions
To maintain consistency across the codebase:
- **`recipe_location`** (str): A string that can be either a Git URI or a filesystem path
- **`recipe_path`** (Path): A resolved filesystem Path object pointing to a recipe directory
- **`recipe`** (Recipe): A Recipe model object
- **`recipes`** (list[Recipe]): A list of Recipe objects

This ensures clear distinction between:
1. User input (location strings that need resolution)
2. Filesystem paths (resolved local directories)
3. Domain objects (Recipe instances)

### URI to Directory Mapping
- Replace special characters: `/` → `_`, `:` → `_`, `@` → `_`
- Preserve dots for domains
- Ensure Windows compatibility (no colons except drive letters)
- Examples:
  - `https://github.com/user/repo.git@main` → `github.com_user_repo_main`
  - `https://github.com/user/repo.git@v1.2.3` → `github.com_user_repo_v1.2.3`

### Clone Strategy
- **For branches**: Use shallow clone
  ```bash
  git clone --depth 1 --branch <branch> <uri> <target>
  ```
- **For tags**: Clone with tag history
  ```bash
  git clone --depth 1 --branch <tag> <uri> <target>
  ```
- Default to main/master if no ref specified
- Use `--single-branch` for efficiency
- Auto-detect if ref is a tag using `git ls-remote --tags`

### Error Handling
- Git not available: Clear error message with installation instructions
- Network errors: Suggest checking connectivity
- Invalid URI: Detailed validation error
- Permission errors: Suggest authentication setup

### Logging
- INFO: "Cloning repository from {uri}..."
- INFO: "Checking out {ref_type} '{ref}' in {path}..."
- INFO: "Updating repository at {path}..." (only for branches)
- INFO: "Using cached repository at {path} (tags are immutable)"
- ERROR: Detailed error messages with recovery suggestions

## Testing Strategy

### Unit Tests
- URI parsing with various formats
- Cache path generation
- Git availability detection

### Integration Tests
- Mock Git repositories
- Test clone and update scenarios
- Test layer resolution with Git URIs

### Manual Testing
- Real GitHub/GitLab repositories
- Various URI formats
- Cross-platform testing (Linux, macOS, Windows)

## Security Considerations
- Validate URIs to prevent directory traversal
- Use subprocess with shell=False for Git commands
- Don't store credentials - rely on system Git configuration

## Future Enhancements (Not in scope)
- Authentication token support
- Progress indicators for large clones
- Parallel cloning for multiple layers
- Sparse checkout for large repositories
- Git submodule support