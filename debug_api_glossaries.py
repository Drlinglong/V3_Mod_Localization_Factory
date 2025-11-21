import requests
import json

try:
    response = requests.get('http://localhost:8000/api/glossaries/stellaris')
    data = response.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
