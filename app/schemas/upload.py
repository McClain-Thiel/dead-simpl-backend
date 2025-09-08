from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from ..db.models import UploadTask

class UploadBase(BaseModel):
    task: UploadTask = Field(..., description="The task associated with the upload")
    filename: str
    size: int
    content_type: str

class UploadCreate(UploadBase):
    storage_url: str

class Upload(UploadBase):
    id: UUID
    user_id: UUID
    storage_url: str
    created_at: datetime

    class Config:
        orm_mode = True 