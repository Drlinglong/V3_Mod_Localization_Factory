from fastapi import APIRouter, HTTPException
from scripts.core.prompt_manager import prompt_manager
from scripts.schemas.prompts import UpdateSystemPromptRequest, UpdateCustomPromptRequest, ResetPromptRequest, UpdateFormatPromptRequest

router = APIRouter()

@router.get("/api/prompts")
def get_prompts():
    """Returns all system prompts (default/overridden) and the custom global prompt."""
    return prompt_manager.get_all_prompts()

@router.post("/api/prompts/system")
def update_system_prompt(payload: UpdateSystemPromptRequest):
    """Updates (overrides) the system prompt for a specific game."""
    try:
        prompt_manager.save_system_prompt_override(payload.game_id, payload.prompt_template)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/prompts/custom")
def update_custom_prompt(payload: UpdateCustomPromptRequest):
    """Updates the persistent custom global prompt."""
    try:
        prompt_manager.save_custom_global_prompt(payload.custom_prompt)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/prompts/format")
def update_format_prompt(payload: UpdateFormatPromptRequest):
    """Updates (overrides) the format prompt for a specific game."""
    try:
        prompt_manager.save_format_prompt_override(payload.game_id, payload.format_prompt)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/prompts/reset")
def reset_prompts(payload: ResetPromptRequest):
    """Resets prompts to their default values."""
    try:
        prompt_manager.reset_prompts(
            game_id=payload.game_id,
            reset_all=payload.reset_all,
            reset_custom=payload.reset_custom,
            reset_format=payload.reset_format
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
