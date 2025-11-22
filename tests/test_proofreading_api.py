import os
import shutil
import pytest
from fastapi.testclient import TestClient
from scripts.web_server import app, SOURCE_DIR, DEST_DIR

client = TestClient(app)

# Setup dummy data
TEST_MOD_NAME = "test_proofreading_mod"
TEST_FILE_NAME = "test_l_english.yml"
TEST_CONTENT = 'l_english:\n key: "value"'

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    # Setup
    mod_dir = os.path.join(SOURCE_DIR, TEST_MOD_NAME)
    os.makedirs(mod_dir, exist_ok=True)
    
    # Create a localization file
    loc_dir = os.path.join(mod_dir, "localization", "english")
    os.makedirs(loc_dir, exist_ok=True)
    
    with open(os.path.join(loc_dir, TEST_FILE_NAME), "w", encoding="utf-8-sig") as f:
        f.write(TEST_CONTENT)
        
    yield
    
    # Teardown
    if os.path.exists(mod_dir):
        shutil.rmtree(mod_dir)
    
    # Clean up dest dir if created
    dest_mod_dir = os.path.join(DEST_DIR, f"zh-CN-{TEST_MOD_NAME}")
    if os.path.exists(dest_mod_dir):
        shutil.rmtree(dest_mod_dir)

def test_list_mods():
    response = client.get("/api/proofreading/mods")
    assert response.status_code == 200
    assert TEST_MOD_NAME in response.json()

def test_list_files():
    # Assuming game_id 1 (Vic3) uses 'localization' folder
    response = client.get(f"/api/proofreading/files?mod_name={TEST_MOD_NAME}&game_id=1")
    assert response.status_code == 200
    files = response.json()
    assert any(TEST_FILE_NAME in f for f in files)

def test_get_content():
    # Get the relative path first
    response = client.get(f"/api/proofreading/files?mod_name={TEST_MOD_NAME}&game_id=1")
    files = response.json()
    rel_path = next(f for f in files if TEST_FILE_NAME in f)
    
    response = client.get(f"/api/proofreading/content?mod_name={TEST_MOD_NAME}&file_path={rel_path}&target_lang=zh-CN")
    assert response.status_code == 200
    data = response.json()
    assert "l_english" in data["original_content"]
    assert data["translation_content"] == "" # Should be empty initially

def test_save_content():
    # Get relative path
    response = client.get(f"/api/proofreading/files?mod_name={TEST_MOD_NAME}&game_id=1")
    files = response.json()
    rel_path = next(f for f in files if TEST_FILE_NAME in f)
    
    new_content = 'l_simp_chinese:\n key: "值"'
    
    payload = {
        "file_path": "", # New file
        "content": new_content,
        "mod_name": TEST_MOD_NAME,
        "target_lang": "zh-CN",
        "relative_path": rel_path
    }
    
    response = client.post("/api/proofreading/save", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify it was saved by reading it back
    response = client.get(f"/api/proofreading/content?mod_name={TEST_MOD_NAME}&file_path={rel_path}&target_lang=zh-CN")
    assert response.status_code == 200
    data = response.json()
    assert data["translation_content"] == new_content
