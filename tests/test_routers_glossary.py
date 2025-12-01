import pytest
from fastapi.testclient import TestClient
from scripts.web_server import app

client = TestClient(app)

def test_get_glossaries():
    # Assuming 'stellaris' is a valid game_id
    response = client.get("/api/glossaries/stellaris")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_glossary():
    response = client.post("/api/glossary/search", json={
        "query": "Empire",
        "scope": "game",
        "game_id": "stellaris"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "entries" in data
    assert isinstance(data["entries"], list)
