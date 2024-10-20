import logging
from pathlib import Path

import pytest


# change logging settings for testing
@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.ERROR, logger="cels")
    caplog.set_level(logging.DEBUG, logger="spekulatio")

@pytest.fixture(scope="session")
def fixtures_path():
    return Path(__file__).parent / "_fixtures"

@pytest.fixture(scope="function")
def output_path(tmp_path_factory):
    output_path = tmp_path_factory.mktemp("output")
    return output_path
