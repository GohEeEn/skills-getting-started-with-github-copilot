import pytest
import copy
from fastapi.testclient import TestClient
import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    app_module.activity_service.data = copy.deepcopy(app_module.activities_initial)


def test_get_activities_returns_200():
    # Arrange
    client = TestClient(app_module.app)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_for_nonexistent_activity_raises_404():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result


def test_signup_for_existing_participant_raises_400():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result


def test_signup_when_activity_full_raises_400():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Tennis Club"  # Max 10, has 1 participant
    email = "newstudent@mergington.edu"
    
    # Fill the activity
    for i in range(9):  # Add 9 more to reach max 10
        client.post(f"/activities/{activity}/signup", params={"email": f"student{i}@mergington.edu"})
    
    # Act - try to add 11th
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result


def test_unregister_for_activity_removes_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_for_nonexistent_activity_raises_404():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result


def test_unregister_for_not_signed_up_raises_400():
    # Arrange
    client = TestClient(app_module.app)
    activity = "Chess Club"
    email = "notsignedup@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result


def test_root_redirects_to_index():
    # Arrange
    client = TestClient(app_module.app, follow_redirects=False)
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"