from pydantic import BaseModel

class UpdateConfigRequest(BaseModel):
    action: str
    path: str

class UpdateApiKeyRequest(BaseModel):
    provider_id: str
    api_key: str
