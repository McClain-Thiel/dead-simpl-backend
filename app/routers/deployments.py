from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import DBSessionDependency, get_current_user
from ..db.models import Deployment, User
from ..schemas.deployment import Deployment as DeploymentSchema, DeploymentCreate, DeploymentUpdate
from ..db import crud

router = APIRouter(
    prefix="/api/deployments",
    tags=["Deployments"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=DeploymentSchema)
def create_deployment(deployment: DeploymentCreate, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Create a new deployment."""
    return crud.create_deployment(db=db, deployment=deployment, user_id=user.id)

@router.get("/", response_model=List[DeploymentSchema])
def read_deployments(db: DBSessionDependency, user: User = Depends(get_current_user), skip: int = 0, limit: int = 100):
    """Retrieve deployments for the current user."""
    deployments = crud.get_deployments_by_user(db=db, user_id=user.id, skip=skip, limit=limit)
    return deployments

@router.get("/{deployment_id}", response_model=DeploymentSchema)
def read_deployment(deployment_id: UUID, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Retrieve a specific deployment."""
    db_deployment = crud.get_deployment(db=db, deployment_id=deployment_id, user_id=user.id)
    if db_deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return db_deployment

@router.put("/{deployment_id}", response_model=DeploymentSchema)
def update_deployment(deployment_id: UUID, deployment: DeploymentUpdate, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Update a deployment."""
    db_deployment = crud.update_deployment(db=db, deployment_id=deployment_id, deployment_update=deployment, user_id=user.id)
    if db_deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return db_deployment

@router.delete("/{deployment_id}", response_model=DeploymentSchema)
def delete_deployment(deployment_id: UUID, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Delete a deployment."""
    db_deployment = crud.delete_deployment(db=db, deployment_id=deployment_id, user_id=user.id)
    if db_deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return db_deployment 