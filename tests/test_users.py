# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users_unauthorized():
    response = client.get("/users")
    # Expecting 401 if no token provided
    assert response.status_code == 401

def test_register_user():
    # Register a new user
    data = {"username": "testuser", "password": "testpass"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
