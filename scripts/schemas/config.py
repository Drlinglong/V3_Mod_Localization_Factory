from pydantic import BaseModel

from typing import Optional, List

class UpdateConfigRequest(BaseModel):
    action: Optional[str] = None
    path: Optional[str] = None
    translation_dirs: Optional[List[str]] = None

class UpdateApiKeyRequest(BaseModel):
    provider_id: str
    api_key: str
