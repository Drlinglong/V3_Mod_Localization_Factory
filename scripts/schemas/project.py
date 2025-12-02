from pydantic import BaseModel

class CreateProjectRequest(BaseModel):
    name: str
    folder_path: str
    game_id: str
    source_language: str = "english"

class UpdateProjectStatusRequest(BaseModel):
    status: str

class UpdateProjectNotesRequest(BaseModel):
    notes: str
