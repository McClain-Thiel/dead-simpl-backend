from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class APIKeyBase(BaseModel):
    name: str = Field(..., description="A user-friendly name for the API key")
    scopes: Optional[List[str]] = Field(None, description="List of scopes for the API key")

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: UUID
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class APIKeyWithSecret(APIKey):
    key_secret: str = Field(..., description="The full API key secret (only returned on creation)") 