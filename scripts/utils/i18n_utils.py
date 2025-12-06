from scripts.schemas.common import LanguageCode, GameType

def iso_to_paradox(iso_code: str) -> str:
    """
    Converts Standard ISO Language Code (e.g. 'zh-CN') to Paradox Legacy Key (e.g. 'simp_chinese').
    Used when the system (Database) talks to the Disk (Paradox Files).
    """
    if not iso_code:
        return "english"
        
    try:
        # Pydantic Enum has the mapping logic inside? 
        # Actually LanguageCode.to_paradox() was implemented in common.py!
        # We can just reuse that, but this helper provides a clean import for random scripts
        # and handles raw strings.
        
        # Try to parse into Enum first
        lang_enum = LanguageCode.from_str(iso_code)
        return lang_enum.to_paradox()
    except ValueError:
        # Fallback for unknown codes, just lower it
        return iso_code.lower()

def paradox_to_iso(paradox_code: str) -> str:
    """
    Converts Paradox Legacy Key (e.g. 'simp_chinese') to Standard ISO Code (e.g. 'zh-CN').
    Used when the Disk talks back to the System.
    """
    if not paradox_code:
        return "en"
        
    # LanguageCode.from_str handles mapping FROM paradox strings TO Enum values (which correspond to ISO)
    try:
        return LanguageCode.from_str(paradox_code).value
    except ValueError:
        return "en"

def normalize_game_id(game_id: str) -> str:
    """
    Normalizes Game IDs (e.g. 'Victoria 3' -> 'vic3').
    """
    return GameType.from_str(game_id).value
