import requests
import json
import os

# Configuration
API_URL = "http://127.0.0.1:8000/api/proofread"
PROJECT_ID = "Test_Project_Remis_Vic3" # Assuming this is the ID
FILE_ID = "remis_demo_l_english.yml" # This needs to be the File ID, not name.

# We need to find the File ID first.
# Let's assume the file ID is the filename for now, or we can fetch the project files first.

def get_file_id():
    try:
        resp = requests.get(f"http://127.0.0.1:8000/api/project/{PROJECT_ID}/files")
        if resp.status_code == 200:
            files = resp.json()
            for f in files:
                if "l_english.yml" in f['file_path']:
                    print(f"Found file: {f['file_path']}, ID: {f['file_id']}")
                    return f['file_id']
    except Exception as e:
        print(f"Failed to fetch files: {e}")
    return None

def trigger_proofread():
    file_id = get_file_id()
    if not file_id:
        print("Could not find file ID for English file.")
        return

    url = f"{API_URL}/{PROJECT_ID}/{file_id}"
    print(f"Calling: {url}")
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            print("Success!")
            print(f"AI Content Length: {len(data.get('ai_content', ''))}")
            print(f"AI Content Preview: {data.get('ai_content', '')[:100]}")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_proofread()
