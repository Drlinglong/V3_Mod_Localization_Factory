from typing import List, Dict, Any
from pydantic import BaseModel, field_validator
from scripts.schemas.common import LanguageCode

class SaveProofreadingRequest(BaseModel):
    project_id: str
    file_id: str
    entries: List[Dict[str, Any]]
    content: str = "" # Legacy support
    target_language: LanguageCode = LanguageCode.ZH_CN

    @field_validator('target_language', mode='before')
    @classmethod
    def normalize_lang(cls, v):
        if isinstance(v, str):
            return LanguageCode.from_str(v)
        return v

