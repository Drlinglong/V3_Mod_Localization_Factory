import requests
import json

BASE_URL = "http://localhost:8000"

def check_game_mapping():
    try:
        # Fetch Config
        print("Fetching config...")
        config_res = requests.get(f"{BASE_URL}/api/config")
        config = config_res.json()
        game_profiles = config.get("game_profiles", {})
        print(f"Game Profiles Keys: {list(game_profiles.keys())}")
        
        # Fetch Projects
        print("Fetching projects...")
        projects_res = requests.get(f"{BASE_URL}/api/projects")
        projects = projects_res.json()
        
        target_project_name = "提供更多商船"
        target_project = next((p for p in projects if p['name'] == target_project_name), None)
        
        if not target_project:
            print(f"Project '{target_project_name}' not found!")
            return

        print(f"Project Found: {target_project['name']}")
        print(f"Project Game ID: '{target_project['game_id']}' (Type: {type(target_project['game_id'])})")
        
        # Simulate Lookup
        game_id = target_project['game_id']
        profile = game_profiles.get(game_id)
        
        if profile:
            print(f"Direct Lookup Success: {profile['name']}")
        else:
            print("Direct Lookup Failed!")
            # Try finding by ID
            found_by_id = None
            for key, p in game_profiles.items():
                if p.get('id') == game_id:
                    found_by_id = p
                    break
            
            if found_by_id:
                print(f"Lookup by ID Success: {found_by_id['name']}")
            else:
                print("Lookup by ID Failed!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_game_mapping()
