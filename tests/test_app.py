import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app as fastapi_app


client = TestClient(fastapi_app)


# Keep an immutable copy of the initial activities so tests can restore state
_ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield


def test_root_redirect_location():
    # Arrange
    # (client fixture already configured)

    # Act
    resp = client.get("/", follow_redirects=False)

    # Assert
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    # Arrange
    email = "test.student@mergington.edu"

    # Act
    resp = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_already_signed_up():
    # Arrange
    email = _ORIGINAL_ACTIVITIES["Chess Club"]["participants"][0]

    # Act
    resp = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400


def test_signup_for_activity_not_found():
    # Arrange

    # Act
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@y.com"})

    # Assert
    assert resp.status_code == 404


def test_unregister_participant_success():
    # Arrange
    email = _ORIGINAL_ACTIVITIES["Programming Class"]["participants"][0]

    # Act
    resp = client.delete("/activities/Programming Class/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in app_module.activities["Programming Class"]["participants"]


def test_unregister_participant_not_found():
    # Arrange

    # Act
    resp = client.delete("/activities/Programming Class/participants", params={"email": "not@there.com"})

    # Assert
    assert resp.status_code == 404
