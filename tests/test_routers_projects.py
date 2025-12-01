import pytest
from fastapi.testclient import TestClient
from scripts.web_server import app

client = TestClient(app)

def test_read_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_project_invalid_path():
    # Test creating a project with a non-existent path
    response = client.post("/api/project/create", json={
        "name": "Test Project",
        "folder_path": "C:/NonExistentPath/Mod",
        "game_id": "stellaris"
    })
    # Should fail because path doesn't exist
    assert response.status_code == 404
