
from filecmp import dircmp

from spekulatio.logs import log
from spekulatio.operations import build


def compare_output(generated_output_path, expected_output_path) -> list:
    """Return a list of differences between two directories recursively."""

    def process_result(result):
        """Recursively convert comparison results to list."""
        diff = []
        for name in result.diff_files:
            diff.append(f"Not matching: {name}")
        for name in result.left_only:
            diff.append(f"Only in generated output {generated_output_path.name}: {name}")
        for name in result.right_only:
            diff.append(f"Only in expected output {expected_output_path.name}: {name}")
        for subdir_result in result.subdirs.values():
            subdir_diff = process_result(subdir_result)
            diff.extend(subdir_diff)
        return diff

    result = dircmp(generated_output_path, expected_output_path)
    diff = process_result(result)
    return diff

def test_project(project_path, output_path):
    """Test complete build of a project."""

    # get directories
    input_path = project_path / "input"
    expected_output_path = project_path / "output"

    # build
    build(input_path, output_path)

    # compare
    diff = compare_output(output_path, expected_output_path)
    assert not diff
