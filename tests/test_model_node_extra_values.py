import yaml

from spekulatio.operations import get_layers
from spekulatio.operations import create_tree
from spekulatio.operations import write_tree


def test_extra_values(fixtures_path, output_path):
    layers = get_layers(
        fixtures_path / "extra-values",
        values_file="_vals.yaml",
        extra_values_file="_vals.extra.yaml",
    )
    root = create_tree(layers)
    write_tree(output_path, root, cache=False)

    content = (output_path / "foo.yaml").read_text()
    data = yaml.safe_load(content)
    assert data["numbers"] == [0, 1, 2]
