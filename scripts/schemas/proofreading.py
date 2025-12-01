from typing import List, Dict, Any
from pydantic import BaseModel

class SaveProofreadingRequest(BaseModel):
    project_id: str
    file_id: str
    entries: List[Dict[str, Any]]
    content: str = "" # Legacy support
