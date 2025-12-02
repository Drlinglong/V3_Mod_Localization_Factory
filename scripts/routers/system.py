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

class SaveFileRequest(BaseModel):
    file_path: str
    content: str

@router.post("/save_file")
async def save_file(request: SaveFileRequest):
    """
    Saves content to a local file with UTF-8-SIG encoding.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(request.file_path), exist_ok=True)
        
        with open(request.file_path, 'w', encoding='utf-8-sig') as f:
            f.write(request.content)
            
        logger.info(f"Saved file: {request.file_path}")
        return {"status": "success", "message": "File saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save file {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
class PatchEntry(BaseModel):
    key: str
    value: str
    line_number: int | None = None

class PatchFileRequest(BaseModel):
    file_path: str
    entries: list[PatchEntry]

@router.post("/patch_file")
async def patch_file(request: PatchFileRequest):
    """
    Patches a localization file by replacing values at specific lines.
    Preserves comments and structure.
    """
    import re
    
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Read all lines
        with open(request.file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # Regex to find the value part: key:0 "value" -> matches "value"
        # We look for the first quote after the key (simplified) or just the last pair of quotes
        # A robust regex for Paradox loc:  ^\s*key:0\s*"(.*)"\s*(#.*)?$
        # But we only want to replace the content inside the quotes.
        
        modified_lines = lines[:]
        new_entries = []

        for entry in request.entries:
            if entry.line_number is not None and 1 <= entry.line_number <= len(modified_lines):
                # Coordinate Strike
                idx = entry.line_number - 1
                line = modified_lines[idx]
                
                # Verify key presence to be safe (optional but recommended)
                # if entry.key not in line: logger.warning(...) 

                # Replace value: look for the pattern "..."
                # We use a non-greedy match for the content inside quotes
                # This regex matches: (anything before first quote) " (content) " (anything after)
                # We replace group 2 with new value.
                
                # Paradox loc format: key:version "value"
                # We want to replace "value" with "new_value"
                
                # Escape the new value for quotes
                safe_value = entry.value.replace('"', '\\"')
                
                # Regex: Find the first quote, then everything until the last quote (handling escaped quotes is hard with simple regex)
                # Simplified approach: Paradox files usually have one pair of outer quotes.
                # Let's assume standard format:  key:0 "VALUE" ...
                
                # Pattern: (.*?:\d+\s*") (.*) ("\s*.*)
                # This might be risky if value contains quotes. 
                # Better: Use the fact that we know the line structure.
                
                # Let's try to find the indices of the first and last quote
                first_quote = line.find('"')
                last_quote = line.rfind('"')
                
                if first_quote != -1 and last_quote != -1 and first_quote < last_quote:
                    # Reconstruct line
                    prefix = line[:first_quote+1]
                    suffix = line[last_quote:]
                    modified_lines[idx] = f"{prefix}{safe_value}{suffix}"
                else:
                    logger.warning(f"Could not find quotes in line {entry.line_number}: {line.strip()}")
            else:
                # New entry or invalid line number
                new_entries.append(entry)

        # Append new entries
        if new_entries:
            if modified_lines and not modified_lines[-1].endswith('\n'):
                modified_lines[-1] += '\n'
            
            for entry in new_entries:
                # Default format for new entries
                modified_lines.append(f' {entry.key}:0 "{entry.value}"\n')

        # Write back
        with open(request.file_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(modified_lines)

        logger.info(f"Patched file: {request.file_path}")
        return {"status": "success", "message": "File patched successfully"}

    except Exception as e:
        logger.error(f"Failed to patch file {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to patch file: {str(e)}")
