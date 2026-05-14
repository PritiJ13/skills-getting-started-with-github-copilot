import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_new_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up alex@mergington.edu for Chess Club"
    assert "alex@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "nobody@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
