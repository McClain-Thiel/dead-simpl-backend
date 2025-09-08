from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvalCreate(BaseModel):
    """Schema for creating a new evaluation."""
    model_id: UUID = Field(..., description="The ID of the model to evaluate.")
    dataset_id: UUID = Field(..., description="The ID of the dataset to use for evaluation.")
    metrics: List[str] = Field(..., description="A list of metrics to compute.")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration for the evaluation.")

class EvalResult(BaseModel):
    """Schema for returning evaluation results."""
    eval_id: UUID
    status: str = Field(..., description="The status of the evaluation (e.g., pending, running, completed, failed).")
    scores: Dict[str, float] = Field(..., description="A dictionary of computed metric scores.")
    report_url: Optional[str] = Field(None, description="A URL to a detailed report of the evaluation.")
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True 