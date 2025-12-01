from pydantic import BaseModel

class CreateProjectRequest(BaseModel):
    name: str
    folder_path: str
    game_id: str

class UpdateProjectStatusRequest(BaseModel):
    status: str

class UpdateProjectNotesRequest(BaseModel):
    notes: str
