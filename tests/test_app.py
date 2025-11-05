from fastapi.testclient import TestClient
import pytest
from src.app import app

client = TestClient(app)

def test_read_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Check if we have the expected activities structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    activity_name = "Art Club"
    email = "test@example.com"
    
    # First, make sure the activity exists
    response = client.get("/activities")
    activities = response.json()
    assert activity_name in activities
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    
    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_unregister_from_activity():
    activity_name = "Art Club"
    email = "test@example.com"
    
    # First, sign up for the activity
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    
    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_signup_invalid_activity():
    response = client.post("/activities/InvalidActivity/signup?email=test@example.com")
    assert response.status_code == 404

def test_signup_full_activity():
    activity_name = "Art Club"
    
    # Get current participants
    response = client.get("/activities")
    activities = response.json()
    max_participants = activities[activity_name]["max_participants"]
    
    # Clear existing participants
    for participant in activities[activity_name]["participants"]:
        client.delete(f"/activities/{activity_name}/unregister?email={participant}")
    
    # Fill up the activity
    emails = [f"test{i}@example.com" for i in range(max_participants + 1)]
    
    # Sign up participants until full
    for email in emails[:-1]:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
    
    # Try to sign up one more participant
    response = client.post(f"/activities/{activity_name}/signup?email={emails[-1]}")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]

def test_unregister_not_registered():
    response = client.delete("/activities/Yoga/unregister?email=notregistered@example.com")
    assert response.status_code == 404