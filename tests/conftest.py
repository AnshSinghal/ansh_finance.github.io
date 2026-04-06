import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def disable_throttling(settings):
    settings.DEFAULT_THROTTLE_CLASSES = []
    settings.DEFAULT_THROTTLE_RATES = {}
    with patch("users.throttles.AuthRateThrottle.allow_request", return_value=True):
        yield
