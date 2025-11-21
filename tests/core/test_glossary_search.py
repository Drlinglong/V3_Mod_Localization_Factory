import pytest
import os
import json
from unittest.mock import MagicMock, patch, mock_open
from scripts.web_server import app, _transform_storage_to_frontend_format, SearchGlossaryRequest
from fastapi.testclient import TestClient

client = TestClient(app)

# Mock data
MOCK_GLOSSARY_DATA = {
    "entries": [
        {
            "id": "1",
            "translations": {"en": "Source1", "zh": "Trans1"},
            "metadata": {"remarks": "Note1"},
            "variants": {"en": ["Var1"]},
            "abbreviations": {}
        },
        {
            "id": "2",
            "translations": {"en": "Apple", "zh": "Pingguo"},
            "metadata": {"remarks": "Fruit"},
            "variants": {},
            "abbreviations": {}
        }
    ]
}

def test_transform_format():
    entry = MOCK_GLOSSARY_DATA["entries"][0]
    transformed = _transform_storage_to_frontend_format(entry, "game1", "file1.json")

    assert transformed["source"] == "Source1"
    assert transformed["game_id"] == "game1"
    assert transformed["file_name"] == "file1.json"
    assert transformed["translations"]["zh"] == "Trans1"
    # Verify the weird variant logic is preserved (returns list first, then dict overwrites? No, my implementation returns dict in step 5)
    # Let's check my implementation of _transform...
    # Step 2: new_entry['variants'] = list
    # Step 5: new_entry['variants'] = entry.get('variants') -> dict
    # So it should be a dict.
    assert isinstance(transformed["variants"], dict)
    assert transformed["variants"]["en"] == ["Var1"]

@patch("os.path.isdir")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_GLOSSARY_DATA))
def test_search_glossary_file_scope(mock_file, mock_listdir, mock_isdir):
    # Test searching a specific file
    response = client.post("/api/glossary/search", json={
        "scope": "file",
        "query": "Apple",
        "game_id": "game1",
        "file_name": "file1.json"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["totalCount"] == 1
    assert data["entries"][0]["source"] == "Apple"
    assert data["entries"][0]["game_id"] == "game1"

@patch("os.path.isdir")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_GLOSSARY_DATA))
def test_search_glossary_game_scope(mock_file, mock_listdir, mock_isdir):
    # Setup mocks to simulate multiple files in a game
    mock_isdir.return_value = True
    mock_listdir.return_value = ["file1.json", "file2.json"]

    # We need to make sure the mock_open returns data for both files.
    # Since read_data is static in the decorator, it returns the same data for both.
    # So we expect 1 match per file = 2 matches total.

    response = client.post("/api/glossary/search", json={
        "scope": "game",
        "query": "Apple",
        "game_id": "game1"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["totalCount"] == 2
    assert data["entries"][0]["game_id"] == "game1"

@patch("os.path.isdir")
@patch("os.listdir")
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_GLOSSARY_DATA))
def test_search_glossary_all_scope(mock_file, mock_listdir, mock_isdir):
    # Setup mocks to simulate multiple games
    mock_isdir.return_value = True

    # Mock listdir to return games for root, then files for games
    # This is tricky with a single mock_listdir.
    # Side effect: if path ends with GLOSSARY_DIR, return games. Else return files.

    def side_effect_listdir(path):
        if path.endswith("glossary"): # simplified check
            return ["game1", "game2"]
        return ["file1.json"]

    mock_listdir.side_effect = side_effect_listdir

    response = client.post("/api/glossary/search", json={
        "scope": "all",
        "query": "Apple"
    })

    assert response.status_code == 200
    data = response.json()
    # 2 games * 1 file each * 1 match each = 2 matches
    assert data["totalCount"] == 2
    assert data["entries"][0]["source"] == "Apple"
