import uuid
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_current_user
from ..schemas.eval import EvalCreate, EvalResult

router = APIRouter(
    prefix="/api/evals",
    tags=["Evaluations"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=EvalResult)
def create_eval(eval_create: EvalCreate):
    """
    Create a new evaluation (placeholder).
    """
    # This is a placeholder and does not interact with the database.
    new_eval_id = uuid.uuid4()
    return EvalResult(
        eval_id=new_eval_id,
        status="pending",
        scores={},
        created_at=datetime.utcnow()
    )

@router.get("/{eval_id}", response_model=EvalResult)
def get_eval_result(eval_id: UUID):
    """
    Get evaluation results by ID (placeholder).
    """
    # This is a placeholder and returns dummy data.
    if str(eval_id) == "00000000-0000-0000-0000-000000000001":
        return EvalResult(
            eval_id=eval_id,
            status="completed",
            scores={"accuracy": 0.95, "f1_score": 0.92},
            report_url=f"https://example.com/reports/{eval_id}",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
    
    raise HTTPException(status_code=404, detail="Evaluation not found") 