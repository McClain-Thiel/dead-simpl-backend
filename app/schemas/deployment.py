from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from ..db.models import DeploymentStatus

class DeploymentBase(BaseModel):
    model_version_id: UUID = Field(..., description="ID of the model version to deploy")
    autoscale: Optional[Dict[str, Any]] = Field(None, description="Autoscaling configuration")
    config: Optional[Dict[str, Any]] = Field(None, description="Deployment configuration")

class DeploymentCreate(DeploymentBase):
    endpoint_slug: str = Field(..., description="Unique slug for the deployment endpoint")

class DeploymentUpdate(BaseModel):
    autoscale: Optional[Dict[str, Any]] = Field(None, description="Autoscaling configuration")
    config: Optional[Dict[str, Any]] = Field(None, description="Deployment configuration")

class Deployment(DeploymentBase):
    id: UUID
    user_id: UUID
    status: DeploymentStatus
    endpoint_slug: str
    created_at: datetime

    class Config:
        orm_mode = True 