from typing import List, Optional
from pydantic import BaseModel

class CheckpointStatusRequest(BaseModel):
    mod_name: str
    target_lang_codes: List[str]

class CustomLangConfig(BaseModel):
    name: str
    code: str
    key: str
    folder_prefix: str

class InitialTranslationRequest(BaseModel):
    project_id: str
    source_lang_code: str
    target_lang_codes: List[str] = ["zh-CN"]
    api_provider: str = "gemini"
    model: str = "gemini-pro"
    mod_context: Optional[str] = ""
    selected_glossary_ids: Optional[List[int]] = []
    use_main_glossary: bool = True
    clean_source: bool = False
    custom_lang_config: Optional[CustomLangConfig] = None

class TranslationRequestV2(BaseModel):
    project_path: str
    game_profile_id: str
    source_lang_code: str
    target_lang_codes: List[str]
    api_provider: str
    mod_context: Optional[str] = ""
    selected_glossary_ids: Optional[List[int]] = []
    model_name: Optional[str] = None
    use_main_glossary: bool = True
    clean_source: bool = False
    is_existing_source: bool = False
    custom_lang_config: Optional[CustomLangConfig] = None
