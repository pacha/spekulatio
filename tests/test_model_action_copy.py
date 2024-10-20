
from spekulatio.operations import build

def test_action_copy(fixtures_path, output_path):

    # generate ouput
    build(fixtures_path / "action-copy", output_path)

    # check there's only one directory and one file in output
    assert [path.name for path in output_path.iterdir()] == ["foo"]

    dir_path = output_path / "foo"
    assert [path.name for path in dir_path.iterdir()] == ["BAR.TXT"]

    file_path = output_path / "foo" / "BAR.TXT"
    assert file_path.read_text() == "foobar\n"
