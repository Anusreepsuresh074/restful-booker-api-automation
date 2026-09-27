import base64
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.core.api_base import ApiBase
from src.helper.auth_helper import AuthHelper
from src.helper.booking_helper import BookingHelper
from src.helper.ping_helper import PingHelper

_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "reports" / "created-resources.jsonl"


@pytest.fixture(scope="session")
def api_base(config):
    return ApiBase(config)


@pytest.fixture(scope="session")
def ping_helper(api_base):
    return PingHelper(api_base)


@pytest.fixture(scope="session")
def auth_helper(api_base):
    return AuthHelper(api_base)


@pytest.fixture(scope="session")
def booking_helper(api_base):
    return BookingHelper(api_base)


@pytest.fixture(scope="session")
def auth_token(auth_helper):
    response = auth_helper.authenticate()
    return response.json()["token"]


@pytest.fixture(scope="session")
def auth_cookie_header(auth_token):
    return AuthHelper.cookie_header(auth_token)


@pytest.fixture(scope="session")
def invalid_auth_cookie_header(auth_token):
    mutated = auth_token[:-1] + ("x" if auth_token[-1:] != "x" else "y")
    return AuthHelper.cookie_header(mutated)


@pytest.fixture(scope="session")
def basic_auth_wrong_password_header():
    username = os.environ["AUTH_USERNAME"]
    credentials = f"{username}:wrong-password".encode()
    encoded = base64.b64encode(credentials).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


@pytest.fixture(scope="session")
def resource_registry(config):
    """Persists created-resource entries to reports/created-resources.jsonl immediately, so a
    mid-run crash doesn't lose track of what was created. `teardown` (separate skill, explicit
    user confirmation only) is the only thing that ever clears entries from this file."""

    def record(resource_type: str, resource_id) -> None:
        _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "resource_type": resource_type,
            "id": resource_id,
            "environment": config.env,
            "created_at": datetime.now(UTC).isoformat(),
        }
        with open(_REGISTRY_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")

    return record
