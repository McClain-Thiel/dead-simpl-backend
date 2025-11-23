import logging
import os
import tempfile
from datetime import datetime
from uuid import UUID

import mlflow
import pandas as pd
from sqlmodel import Session, select

from app.db.database import db
from app.db.models import EvaluationProfile, EvaluationRun, RunStatus, ScorerDefinition
from app.services.eval.scorer_factory import scorer_factory

logger = logging.getLogger(__name__)


def run_evaluation_task(run_id: UUID):
    """
    Background task to execute the evaluation.
    """
    logger.info(f"Starting evaluation run {run_id}")
    
    # We need a new session for the background thread
    with Session(db.engine) as session:
        run = session.get(EvaluationRun, run_id)
        if not run:
            logger.error(f"Run {run_id} not found")
            return

        try:
            # Update status to PROCESSING
            run.status = RunStatus.PROCESSING
            session.add(run)
            session.commit()
            session.refresh(run)

            # 1. Load Data
            if not os.path.exists(run.dataset_path):
                raise FileNotFoundError(f"Dataset not found at {run.dataset_path}")
            
            # Load CSV
            df = pd.read_csv(run.dataset_path)
            
            # 2. Hydrate Profile & Scorers
            profile = session.get(EvaluationProfile, run.profile_id)
            if not profile:
                raise ValueError(f"Profile {run.profile_id} not found")
            
            scorers = []
            for scorer_id in profile.scorer_ids:
                scorer_def = session.get(ScorerDefinition, scorer_id)
                if scorer_def:
                    scorers.append(scorer_factory(scorer_def))
                else:
                    logger.warning(f"Scorer {scorer_id} not found in profile {profile.name}")

            if not scorers:
                raise ValueError("No valid scorers found for this profile")

            # 3. Run MLflow Evaluation
            with mlflow.start_run() as mlflow_run:
                run.mlflow_run_id = mlflow_run.info.run_id
                
                # Prepare data for mlflow.evaluate
                # We pass the dataframe directly. MLflow will look for 'inputs' column by default.
                # If 'ground_truth' is present, it will be used.
                
                # Use mlflow.genai.evaluate as requested
                eval_result = mlflow.genai.evaluate(
                    data=df,
                    scorers=scorers,
                )
                
                # 4. Digest & Save Results
                # Aggregate metrics
                run.summary_results = eval_result.metrics
                
                # Save row-level details
                # eval_result.tables["eval_results_table"] is the artifact path (e.g. "eval_results_table.json")
                if "eval_results_table" in eval_result.tables:
                    artifact_path = eval_result.tables["eval_results_table"]
                    
                    # Download the artifact to a local temp path to ensure we have it
                    local_path = mlflow.artifacts.download_artifacts(
                        run_id=mlflow_run.info.run_id, 
                        artifact_path=artifact_path
                    )
                    
                    # For this MVP, we store the local path to the downloaded artifact
                    run.row_details_path = local_path

            # Success
            run.status = RunStatus.COMPLETED
            session.add(run)
            session.commit()
            logger.info(f"Run {run_id} completed successfully")

        except Exception as e:
            logger.exception(f"Run {run_id} failed")
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            session.add(run)
            session.commit()
