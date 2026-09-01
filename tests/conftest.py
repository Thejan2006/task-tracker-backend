import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # FastAPI app  TestClient 
    return TestClient(app)