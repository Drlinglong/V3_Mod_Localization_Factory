import os
import subprocess
import platform
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["System"])

class OpenFolderRequest(BaseModel):
    path: str

@router.post("/open_folder")
async def open_folder(request: OpenFolderRequest):
    """
    Opens a local folder in the system's file explorer.
    """
    path = request.path
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
        
        logger.info(f"Opened folder: {path}")
        return {"status": "success", "message": f"Opened {path}"}
    except Exception as e:
        logger.error(f"Failed to open folder {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to open folder: {str(e)}")
