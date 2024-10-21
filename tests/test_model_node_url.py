
from spekulatio.operations import get_layers
from spekulatio.operations import create_tree

def test_url(fixtures_path):
    layers = get_layers(fixtures_path / "traversing")
    root = create_tree(layers)

    dir2 = root / "dir1" / "dir2"
    assert dir2.url == "/dir1/dir2"

    md_file = root / "dir1" / "dir2" / "dir3" / "file.md"
    assert md_file.url == "/dir1/dir2/dir3/file.html"
