from pydantic import BaseModel
from typing import Optional

class UpdateSystemPromptRequest(BaseModel):
    game_id: str
    prompt_template: str

class UpdateCustomPromptRequest(BaseModel):
    custom_prompt: str

class ResetPromptRequest(BaseModel):
    game_id: Optional[str] = None
    reset_all: bool = False
    reset_custom: bool = False
