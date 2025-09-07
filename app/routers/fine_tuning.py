import logging
import uuid
from datetime import datetime, timezone
from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import DBSessionDependency, get_current_user
from ..schemas.fine_tuning import (
    TogetherAISFTJob, 
    ClaudeSFTJob, 
    OpenAISFTJob, 
    FineTuningRun,
    TogetherAISFTRun,
    ClaudeSFTRun,
    OpenAISFTRun,
)
from ..db.models import FineTuneJob, FineTuneRun, Provider, User, UserRank

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/fine-tuning", 
    tags=["Fine-Tuning"],
    dependencies=[Depends(get_current_user)]
)


def _get_and_validate_user(db: DBSessionDependency, user: User) -> User:
    if user.rank not in [UserRank.ADMIN, UserRank.USER]:
        raise HTTPException(status_code=403, detail="User does not have permission to perform this action")
    return user


def _create_sft_job(db: DBSessionDependency, job_input: Union[TogetherAISFTJob, ClaudeSFTJob, OpenAISFTJob], provider: Provider, user_id: UUID) -> FineTuneRun:
    """Helper function to create a new SFT job and its initial run."""
    
    fine_tune_job = FineTuneJob(
        provider=provider,
        base_model=job_input.model,
        config=job_input.model_dump(),
        dataset_file_id=job_input.training_file,
        user_id=user_id,
    )
    db.add(fine_tune_job)
    db.commit()
    db.refresh(fine_tune_job)
    
    run = FineTuneRun(
        job_id=fine_tune_job.id,
        provider_job_id=f"{provider.value}-{uuid.uuid4().hex[:8]}",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return FineTuningRun(
        run_id=str(run.id),
        job_id=str(fine_tune_job.id),
        status=run.status.value,
        created_at=run.created_at.isoformat(),
    )


# Together AI Routes
@router.post("/together-ai", response_model=FineTuningRun)
def create_together_ai_sft_job(job: TogetherAISFTJob, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Create a new Together AI SFT job"""
    _get_and_validate_user(db, user)
    logger.info(f"Creating Together AI SFT job with model: {job.model}")
    return _create_sft_job(db, job, Provider.TOGETHER, user.id)


@router.get("/together-ai/{run_id}", response_model=TogetherAISFTRun)
def get_together_ai_sft_run(run_id: str, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Get status of a Together AI SFT run"""
    _get_and_validate_user(db, user)
    logger.info(f"Getting Together AI SFT run status for: {run_id}")
    
    # Dummy implementation
    return TogetherAISFTRun(
        run_id=run_id,
        job_id="dummy-job-id",
        status="running",
        created_at=datetime.now(timezone.utc).isoformat(),
        progress=0.45,
        estimated_completion="2024-01-01T12:00:00Z",
        metrics={
            "training_loss": 2.34,
            "validation_loss": 2.56,
            "learning_rate": 0.00001,
            "epoch": 2.1
        }
    )


# Claude Routes
@router.post("/claude", response_model=FineTuningRun)
def create_claude_sft_job(job: ClaudeSFTJob, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Create a new Claude SFT job"""
    _get_and_validate_user(db, user)
    logger.info(f"Creating Claude SFT job with model: {job.model}")
    return _create_sft_job(db, job, Provider.ANTHROPIC, user.id)


@router.get("/claude/{run_id}", response_model=ClaudeSFTRun)
def get_claude_sft_run(run_id: str, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Get status of a Claude SFT run"""
    _get_and_validate_user(db, user)
    logger.info(f"Getting Claude SFT run status for: {run_id}")

    # Dummy implementation
    return ClaudeSFTRun(
        run_id=run_id,
        job_id="dummy-job-id",
        status="completed",
        created_at=datetime.now(timezone.utc).isoformat(),
        progress=1.0,
        metrics={
            "final_training_loss": 1.23,
            "final_validation_loss": 1.45,
            "total_training_time": "2h 34m",
            "tokens_processed": 1234567
        }
    )


# OpenAI Routes
@router.post("/openai", response_model=FineTuningRun)
def create_openai_sft_job(job: OpenAISFTJob, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Create a new OpenAI SFT job"""
    _get_and_validate_user(db, user)
    logger.info(f"Creating OpenAI SFT job with model: {job.model}")
    return _create_sft_job(db, job, Provider.OPENAI, user.id)


@router.get("/openai/{run_id}", response_model=OpenAISFTRun)
def get_openai_sft_run(run_id: str, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Get status of an OpenAI SFT run"""
    _get_and_validate_user(db, user)
    logger.info(f"Getting OpenAI SFT run status for: {run_id}")
    
    # Dummy implementation
    return OpenAISFTRun(
        run_id=run_id,
        job_id="dummy-job-id",
        status="failed",
        created_at=datetime.now(timezone.utc).isoformat(),
        progress=0.0,
        error_message="Training file validation failed: Invalid format on line 42",
        metrics={
            "validation_errors": 5,
            "processed_examples": 1250
        }
    )


