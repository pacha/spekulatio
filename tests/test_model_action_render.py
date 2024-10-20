
from spekulatio.operations import build

def test_action_render(fixtures_path, output_path):

    # generate ouput
    build(fixtures_path / "action-render", output_path)

    # check the structure of output
    assert set([path.name for path in output_path.iterdir()]) == set(["foo", "bar"])

    foo_path = output_path / "foo"
    assert [path.name for path in foo_path.iterdir()] == ["with-frontmatter.txt"]

    bar_path = output_path / "bar"
    assert [path.name for path in bar_path.iterdir()] == ["without-frontmatter.txt"]

    # check file contents
    with_frontmatter_path = foo_path / "with-frontmatter.txt"
    assert with_frontmatter_path.read_text() == "red | 300"

    without_frontmatter_path = bar_path / "without-frontmatter.txt"
    assert without_frontmatter_path.read_text() == "red | 3"
