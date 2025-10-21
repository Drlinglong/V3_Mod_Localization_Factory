from pydantic import BaseModel, Field
from typing import List

class TranslationResponse(BaseModel):
    translations: List[str] = Field(description="A list of translated strings. The list must have the same number of elements as the input list.")
