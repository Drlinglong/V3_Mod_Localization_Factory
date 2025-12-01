from fastapi import APIRouter, HTTPException
from scripts.core import workshop_formatter
from scripts.schemas.tools import WorkshopRequest

router = APIRouter()

@router.post("/api/tools/generate_workshop_description")
def generate_workshop_description(payload: WorkshopRequest):
    original_desc = workshop_formatter.get_workshop_item_details(payload.item_id)
    if original_desc is None:
        raise HTTPException(status_code=502, detail="Failed to fetch from Steam Workshop.")
    formatted_bbcode = workshop_formatter.format_description_with_ai(
        original_description=original_desc, **payload.dict()
    )
    if "[AI Formatting Failed" in formatted_bbcode:
         raise HTTPException(status_code=500, detail=f"AI processing failed: {formatted_bbcode}")
    saved_path = workshop_formatter.archive_generated_description(
        project_id=payload.project_id, bbcode_content=formatted_bbcode, workshop_id=payload.item_id
    )
    return {"bbcode": formatted_bbcode, "saved_path": saved_path}
