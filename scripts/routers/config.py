import os
import json
import logging
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

from scripts.app_settings import API_PROVIDERS, get_api_key, get_appdata_config_path
from scripts.schemas.config import UpdateApiKeyRequest

router = APIRouter()

@router.get("/api/api-keys")
def get_api_keys():
    providers = []
    # Reload env to ensure we have the latest keys if they were changed externally
    load_dotenv(override=True)
    
    for provider_id, config in API_PROVIDERS.items():
        env_var = config.get("api_key_env")
        is_keyless = env_var is None
        
        api_key = get_api_key(provider_id, env_var) if env_var else None
        has_key = bool(api_key)
        
        masked_key = None
        if has_key and len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        elif has_key:
            masked_key = "***"
            
        providers.append({
            "id": provider_id,
            "name": provider_id.replace("_", " ").title(),
            "description": config.get("description", ""),
            "is_keyless": is_keyless,
            "has_key": has_key,
            "masked_key": masked_key
        })
    return providers

@router.post("/api/api-keys")
def update_api_key(payload: UpdateApiKeyRequest):
    provider_id = payload.provider_id
    new_key = payload.api_key
    
    if provider_id not in API_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider ID")
        
    config = API_PROVIDERS[provider_id]
    env_var = config.get("api_key_env")
    
    if not env_var:
        raise HTTPException(status_code=400, detail="This provider does not require an API key")
        
    # Save to AppData config.json
    try:
        config_path = get_appdata_config_path()
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {} # Corrupt file, overwrite
        
        if "api_keys" not in config:
            config["api_keys"] = {}
            
        config["api_keys"][provider_id] = new_key
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
    except Exception as e:
        logging.error(f"Failed to save to AppData config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save API key to config file: {str(e)}")
    
    # Update current environment variable immediately
    os.environ[env_var] = new_key
    
    return {"status": "success"}
