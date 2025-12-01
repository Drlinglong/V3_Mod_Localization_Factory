from typing import Optional
from pydantic import BaseModel

class ValidationRequest(BaseModel):
    game_id: str
    content: str
    source_lang_code: Optional[str] = "en_US"
