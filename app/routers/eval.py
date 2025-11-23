import json
import os
import shutil
import tempfile
from typing import List, Optional
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.db.database import get_db_session
from app.db.models import (
    EvaluationProfile,
    EvaluationRun,
    RunStatus,
    ScorerDefinition,
)
from app.schemas.eval import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    RunDetailResponse,
    RunRequest,
    RunResponse,
    ScorerCreate,
    ScorerResponse,
    ScorerUpdate,
    UploadResponse,
)
from app.services.eval.execution import run_evaluation_task

router = APIRouter(prefix="/eval", tags=["eval"])


# --- Scorers ---

@router.get("/scorers", response_model=List[ScorerResponse])
def list_scorers(session: Session = Depends(get_db_session)):
    scorers = session.exec(select(ScorerDefinition)).all()
    return scorers


@router.post("/scorers", response_model=ScorerResponse)
def create_scorer(scorer: ScorerCreate, session: Session = Depends(get_db_session)):
    db_scorer = ScorerDefinition.model_validate(scorer)
    session.add(db_scorer)
    session.commit()
    session.refresh(db_scorer)
    return db_scorer


@router.put("/scorers/{scorer_id}", response_model=ScorerResponse)
def update_scorer(scorer_id: UUID, scorer_update: ScorerUpdate, session: Session = Depends(get_db_session)):
    db_scorer = session.get(ScorerDefinition, scorer_id)
    if not db_scorer:
        raise HTTPException(status_code=404, detail="Scorer not found")
    
    scorer_data = scorer_update.model_dump(exclude_unset=True)
    for key, value in scorer_data.items():
        setattr(db_scorer, key, value)
        
    session.add(db_scorer)
    session.commit()
    session.refresh(db_scorer)
    return db_scorer


@router.delete("/scorers/{scorer_id}")
def delete_scorer(scorer_id: UUID, session: Session = Depends(get_db_session)):
    db_scorer = session.get(ScorerDefinition, scorer_id)
    if not db_scorer:
        raise HTTPException(status_code=404, detail="Scorer not found")
    
    session.delete(db_scorer)
    session.commit()
    return {"ok": True}


# --- Profiles ---

@router.get("/profiles", response_model=List[ProfileResponse])
def list_profiles(session: Session = Depends(get_db_session)):
    profiles = session.exec(select(EvaluationProfile)).all()
    return profiles


@router.post("/profiles", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, session: Session = Depends(get_db_session)):
    db_profile = EvaluationProfile.model_validate(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: UUID, profile_update: ProfileUpdate, session: Session = Depends(get_db_session)):
    db_profile = session.get(EvaluationProfile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile_data = profile_update.model_dump(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
        
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: UUID, session: Session = Depends(get_db_session)):
    db_profile = session.get(EvaluationProfile, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    session.delete(db_profile)
    session.commit()
    return {"ok": True}


# --- Data Ingestion ---

@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    # Save file to a temp location or dedicated upload folder
    # For MVP, using a temp file that persists (not auto-deleted immediately)
    # In production, use S3 or a managed volume.
    
    upload_dir = os.path.join(tempfile.gettempdir(), "dead-simpl-uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Detect columns
    try:
        df = pd.read_csv(file_path, nrows=5) # Read only first few rows
        columns = df.columns.tolist()
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")
        
    return UploadResponse(dataset_id=file_path, detected_columns=columns)


# --- Execution ---

@router.post("/runs", response_model=RunResponse)
def trigger_run(
    run_request: RunRequest, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_db_session)
):
    # Validate Profile
    profile = session.get(EvaluationProfile, run_request.profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    # Validate Dataset
    if not os.path.exists(run_request.dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Create Run Record
    db_run = EvaluationRun(
        profile_id=run_request.profile_id,
        dataset_path=run_request.dataset_id,
        status=RunStatus.PENDING
    )
    session.add(db_run)
    session.commit()
    session.refresh(db_run)
    
    # Dispatch Background Task
    background_tasks.add_task(run_evaluation_task, db_run.id)
    
    return RunResponse(run_id=db_run.id, status=RunStatus.PENDING)


@router.get("/runs", response_model=List[RunDetailResponse])
def list_runs(
    profile_id: Optional[UUID] = None, 
    session: Session = Depends(get_db_session)
):
    query = select(EvaluationRun)
    if profile_id:
        query = query.where(EvaluationRun.profile_id == profile_id)
    
    runs = session.exec(query).all()
    return runs


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: UUID, session: Session = Depends(get_db_session)):
    run = session.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/runs/{run_id}")
def delete_run(run_id: UUID, session: Session = Depends(get_db_session)):
    run = session.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    session.delete(run)
    session.commit()
    return {"ok": True}


# --- Reporting ---

@router.get("/reports/{run_id}/rows")
def get_run_rows(
    run_id: UUID, 
    page: int = 1, 
    page_size: int = 50, 
    session: Session = Depends(get_db_session)
):
    run = session.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    if not run.row_details_path or not os.path.exists(run.row_details_path):
        # If no details yet or file missing
        return {"items": [], "total": 0, "page": page, "pages": 0}
        
    try:
        # Load the JSON/Parquet file
        # For MVP, assuming JSON list of dicts or similar structure
        # If it's a large file, we should use a library that supports chunking or a DB
        # But for "dead simpl", loading into pandas and paginating is fine for moderate sizes
        
        # Check file extension to decide how to read
        if run.row_details_path.endswith(".json"):
            df = pd.read_json(run.row_details_path)
        elif run.row_details_path.endswith(".parquet"):
            df = pd.read_parquet(run.row_details_path)
        else:
             # Fallback or error
             df = pd.read_json(run.row_details_path)
             
        total_items = len(df)
        total_pages = (total_items + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_data = df.iloc[start_idx:end_idx].to_dict(orient="records")
        
        return {
            "items": page_data,
            "total": total_items,
            "page": page,
            "pages": total_pages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report: {e}")
