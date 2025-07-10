import logging
from pathlib import Path

import pytest


# change logging settings for testing
@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.ERROR, logger="cels")
    caplog.set_level(logging.ERROR, logger="py_walk")
    caplog.set_level(logging.ERROR, logger="MARKDOWN")
    caplog.set_level(logging.DEBUG, logger="spekulatio")

@pytest.fixture(scope="session")
def fixtures_path():
    return Path(__file__).parent / "_fixtures"


@pytest.fixture(scope="function")
def output_path(tmp_path_factory):
    output_path = tmp_path_factory.mktemp("output")
    return output_path


def get_projects(directory):
    """Return projects one by one."""
    path = Path(__file__).parent / directory
    yield from path.iterdir()


@pytest.fixture(
    params=get_projects("_projects"), ids=lambda path: path.name, scope="function"
)
def project_path(request):
    return request.param
