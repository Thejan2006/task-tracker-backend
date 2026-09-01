def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_get_categories_unauthorized(client):
    # Log-in  categories  401 
    response = client.get("/categories/")
    assert response.status_code == 401