import uuid
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict

from scripts.shared.services import glossary_manager
from scripts.schemas.glossary import SearchGlossaryRequest, GlossaryEntryCreate, GlossaryEntryIn

logger = logging.getLogger(__name__)

router = APIRouter()

def _transform_storage_to_frontend_format(entry: Dict) -> Dict:
    """
    Transforms a glossary entry from the database storage format to the format
    expected by the frontend.
    """
    new_entry = entry.copy()
    
    # Extract 'en' translation as the source term
    new_entry['source'] = new_entry.get('translations', {}).get('en', '')

    # Extract notes from remarks inside raw_metadata
    new_entry['notes'] = new_entry.get('raw_metadata', {}).get('remarks', '')

    # Pass the full raw_metadata object to the frontend as 'metadata'
    new_entry['metadata'] = new_entry.get('raw_metadata', {})

    # Ensure variants and abbreviations are present
    if 'variants' not in new_entry: new_entry['variants'] = {}
    if 'abbreviations' not in new_entry: new_entry['abbreviations'] = {}
    
    return new_entry

def _transform_entry_to_storage_format(entry: Dict) -> Dict:
    if 'translations' not in entry: entry['translations'] = {}
    if entry.get('source'):
        entry['translations']['en'] = entry['source']
    if 'notes' in entry:
        if 'raw_metadata' not in entry: entry['raw_metadata'] = {}
        entry['raw_metadata']['remarks'] = entry['notes']
        del entry['notes']
    if 'source' in entry: del entry['source']
    return entry

@router.get("/api/glossaries/{game_id}")
def get_game_glossaries(game_id: str):
    return glossary_manager.get_available_glossaries(game_id)

@router.get("/api/glossary/tree")
def get_glossary_tree():
    return glossary_manager.get_glossary_tree_data()

@router.get("/api/glossary/content")
def get_glossary_content(glossary_id: int, page: int = Query(1, alias="page"), pageSize: int = Query(25, alias="pageSize")):
    data = glossary_manager.get_glossary_entries_paginated(glossary_id, page, pageSize)
    transformed_entries = [_transform_storage_to_frontend_format(entry) for entry in data.get("entries", [])]
    return {"entries": transformed_entries, "totalCount": data.get("totalCount", 0)}

@router.post("/api/glossary/search")
def search_glossary(payload: SearchGlossaryRequest):
    glossary_ids_to_search = []
    if payload.scope == 'file':
        if not payload.file_name:
            raise HTTPException(status_code=400, detail="file_name (as key 'game|id|name') is required.")
        try:
            glossary_ids_to_search.append(int(payload.file_name.split('|')[1]))
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid key format.")
    elif payload.scope == 'game':
        if not payload.game_id:
            raise HTTPException(status_code=400, detail="game_id is required.")
        game_glossaries = glossary_manager.get_available_glossaries(payload.game_id)
        glossary_ids_to_search = [g['glossary_id'] for g in game_glossaries]
    elif payload.scope == 'all':
        tree = glossary_manager.get_glossary_tree_data()
        for game_node in tree:
            for file_node in game_node.get('children', []):
                try:
                    glossary_ids_to_search.append(int(file_node['key'].split('|')[1]))
                except (ValueError, IndexError):
                    continue
    if not glossary_ids_to_search:
        return {"entries": [], "totalCount": 0}
    
    logger.debug(f"Searching glossaries {glossary_ids_to_search} for query '{payload.query}'")
    
    result_data = glossary_manager.search_glossary_entries_paginated(
        query=payload.query, glossary_ids=glossary_ids_to_search,
        page=payload.page, page_size=payload.pageSize
    )
    transformed_entries = [_transform_storage_to_frontend_format(entry) for entry in result_data.get("entries", [])]
    return {"entries": transformed_entries, "totalCount": result_data.get("totalCount", 0)}

@router.post("/api/glossary/entry", status_code=201)
def create_glossary_entry(glossary_id: int, payload: GlossaryEntryCreate):
    new_entry_dict = payload.dict()
    new_entry_dict['id'] = str(uuid.uuid4())
    storage_entry = _transform_entry_to_storage_format(new_entry_dict)
    if not glossary_manager.add_entry(glossary_id, storage_entry):
        logger.error(f"Failed to create glossary entry in glossary {glossary_id}")
        raise HTTPException(status_code=500, detail="Failed to create glossary entry.")
    
    logger.info(f"Created new glossary entry {new_entry_dict['id']} in glossary {glossary_id}")
    return new_entry_dict

@router.put("/api/glossary/entry/{entry_id}")
def update_glossary_entry(entry_id: str, payload: GlossaryEntryIn):
    # Placeholder for update logic
    raise HTTPException(status_code=501, detail="Not implemented yet")
