import logging

import pytest


# change logging settings for testing
@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.DEBUG, logger="spekulatio")
