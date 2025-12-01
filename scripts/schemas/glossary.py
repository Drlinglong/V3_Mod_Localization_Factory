from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class GlossaryEntryIn(BaseModel):
    id: str
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict] = {}

class SearchGlossaryRequest(BaseModel):
    scope: str = Field(..., description="Search scope: 'file', 'game', or 'all'")
    query: str = Field(..., description="Search query string")
    game_id: Optional[str] = None
    file_name: Optional[str] = None
    page: int = 1
    pageSize: int = 25

class CreateGlossaryFileRequest(BaseModel):
    game_id: str
    file_name: str

class GlossaryEntryCreate(BaseModel):
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict] = {}
