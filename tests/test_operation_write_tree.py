import time

from spekulatio.operations import get_recipes
from spekulatio.operations import create_tree
from spekulatio.operations import write_tree


def test_cache(fixtures_path, output_path):
    # write output for the first time
    recipes = get_recipes(fixtures_path / "cache")
    root = create_tree(recipes)
    write_tree(output_path, root, cache=False)
    first_timestamp = (output_path / "foo.yaml").stat().st_mtime

    time.sleep(0.001)

    # write output with cache (it shouldn't write anything)
    write_tree(output_path, root, cache=True)
    second_timestamp = (output_path / "foo.yaml").stat().st_mtime
    assert first_timestamp == second_timestamp

    time.sleep(0.001)

    # write output without cache
    write_tree(output_path, root, cache=False)
    third_timestamp = (output_path / "foo.yaml").stat().st_mtime
    assert first_timestamp < third_timestamp
