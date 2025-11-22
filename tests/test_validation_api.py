import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.web_server import app

client = TestClient(app)

def test_validation_api():
    print("Testing /api/validate/localization...")
    
    # Test case 1: Valid content
    valid_content = """
l_english:
 key_1: "Valid Value"
 key_2: "Another Valid Value"
"""
    response = client.post("/api/validate/localization", json={
        "game_id": "1",
        "content": valid_content
    })
    
    if response.status_code == 200:
        results = response.json()
        print(f"Valid content results: {len(results)} issues found (Expected 0 or low info)")
        for r in results:
            print(f" - {r['level']}: {r['message']}")
    else:
        print(f"Failed to call API: {response.status_code} {response.text}")

    # Test case 2: Invalid content (Bad key, missing quotes, etc.)
    invalid_content = """
l_english:
 bad key with spaces: "Value"
 key_3: Value without quotes
 key_4: "Unclosed quotes
"""
    response = client.post("/api/validate/localization", json={
        "game_id": "1",
        "content": invalid_content
    })
    
    if response.status_code == 200:
        results = response.json()
        print(f"\nInvalid content results: {len(results)} issues found")
        for r in results:
            print(f" - Line {r['line_number']} [{r['level']}]: {r['message']} (Key: {r.get('key')})")
    else:
        print(f"Failed to call API: {response.status_code} {response.text}")

if __name__ == "__main__":
    try:
        test_validation_api()
    except Exception as e:
        print(f"Test failed with exception: {e}")
