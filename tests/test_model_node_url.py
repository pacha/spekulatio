from spekulatio.operations import get_recipes
from spekulatio.operations import create_tree


def test_url(fixtures_path):
    recipes = get_recipes(fixtures_path / "traversing")
    root = create_tree(recipes)

    dir2 = root / "dir1" / "dir2"
    assert dir2.url == "/dir1/dir2"

    md_file = root / "dir1" / "dir2" / "dir3" / "file.md"
    assert md_file.url == "/dir1/dir2/dir3/file.html"
