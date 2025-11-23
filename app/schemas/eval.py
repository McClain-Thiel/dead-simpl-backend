from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.models import RunStatus, ScorerType


class ScorerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scorer_type: ScorerType
    configuration: Dict[str, Any]


class ScorerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class ScorerResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    scorer_type: ScorerType
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scorer_ids: List[UUID]


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scorer_ids: Optional[List[UUID]] = None


class ProfileResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    scorer_ids: List[UUID]
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    dataset_id: str
    detected_columns: List[str]


class RunRequest(BaseModel):
    profile_id: UUID
    dataset_id: str
    eval_type: Optional[str] = "rag"  # 'rag', 'chatbot', 'agent'


class RunResponse(BaseModel):
    run_id: UUID
    status: RunStatus


class RunDetailResponse(BaseModel):
    id: UUID
    profile_id: UUID
    dataset_path: str
    mlflow_run_id: Optional[str]
    status: RunStatus
    summary_results: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
