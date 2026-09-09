from fastapi.testclient import TestClient
from app.main import app  # ඔයාගේ main.py තියෙන තැන අනුව 'app.main' වෙනස් කරන්න

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users",  # ඔයාගේ Route එක (උදා: /users හෝ /register)
        json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code in [200, 201]
    assert "id" in response.json()

def test_create_category():
    response = client.post(
        "/categories",
        json={"name": "Work", "description": "Office tasks"}
    )
    assert response.status_code in [200, 201]
    assert response.json()["name"] == "Work"

def test_create_task():
    # this one assumes that a user and category already exist with IDs 1. You may need to adjust this based on your test setup.
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task", 
            "description": "Testing automated scripts", 
            "status": "pending", 
            "category_id": 1, 
            "owner_id": 1
        }
    )
    assert response.status_code in [200, 201]
    assert response.json()["title"] == "Test Task"