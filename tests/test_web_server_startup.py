import pytest
from fastapi.testclient import TestClient
from scripts.web_server import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "欢迎使用P社Mod本地化工厂API"}

def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
