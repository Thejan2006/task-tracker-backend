def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",  
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"


def test_login_user(client):
    
    client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",  
            "password": "password123"
        }
    )
    
   
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()