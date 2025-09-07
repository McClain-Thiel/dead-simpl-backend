from typing import List
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

from ..schemas.deployment import DeploymentCreate, DeploymentUpdate
from ..schemas.api_key import APIKeyCreate
from ..schemas.upload import UploadCreate
from .models import User, Deployment, APIKey, Upload


######################################################
# Generic CRUD operations
######################################################


def update_db_element(
    db: Session, original_element: SQLModel, element_update: BaseModel
) -> BaseModel:
    """Updates an element in database.
    Note that it doesn't take care of user ownership.
    """
    update_data = element_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(original_element, key, value)

    db.add(original_element)
    db.commit()
    db.refresh(original_element)

    return original_element


def delete_db_element(db: Session, element: SQLModel):
    """Deletes an element from database."""
    db.delete(element)
    db.commit()


######################################################
# Specific CRUD operations
######################################################

# User CRUD
def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    return db.exec(select(User).where(User.firebase_uid == firebase_uid)).first()

def create_user(db: Session, firebase_uid: str, email: str, name: str = None):
    db_user = User(firebase_uid=firebase_uid, email=email, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Upload CRUD
def create_upload(db: Session, upload: UploadCreate, user_id: UUID) -> Upload:
    db_upload = Upload(**upload.dict(), user_id=user_id)
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload

def get_upload(db: Session, upload_id: UUID, user_id: UUID) -> Upload:
    return db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == user_id).first()

def get_uploads_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Upload]:
    return db.query(Upload).filter(Upload.user_id == user_id).offset(skip).limit(limit).all()

def delete_upload(db: Session, upload_id: UUID, user_id: UUID) -> Upload:
    db_upload = get_upload(db, upload_id, user_id)
    if not db_upload:
        return None
        
    db.delete(db_upload)
    db.commit()
    return db_upload


# Deployment CRUD
def create_deployment(db: Session, deployment: DeploymentCreate, user_id: UUID) -> Deployment:
    db_deployment = Deployment(**deployment.dict(), user_id=user_id)
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    return db_deployment

def get_deployment(db: Session, deployment_id: UUID, user_id: UUID) -> Deployment:
    return db.query(Deployment).filter(Deployment.id == deployment_id, Deployment.user_id == user_id).first()

def get_deployments_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Deployment]:
    return db.query(Deployment).filter(Deployment.user_id == user_id).offset(skip).limit(limit).all()

def update_deployment(db: Session, deployment_id: UUID, deployment_update: DeploymentUpdate, user_id: UUID) -> Deployment:
    db_deployment = get_deployment(db, deployment_id, user_id)
    if not db_deployment:
        return None
    
    update_data = deployment_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_deployment, key, value)
    
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    return db_deployment

def delete_deployment(db: Session, deployment_id: UUID, user_id: UUID) -> Deployment:
    db_deployment = get_deployment(db, deployment_id, user_id)
    if not db_deployment:
        return None
        
    db.delete(db_deployment)
    db.commit()
    return db_deployment

# API Key CRUD
def create_api_key(db: Session, api_key: APIKeyCreate, user_id: UUID, key_hash: str, key_prefix: str) -> APIKey:
    db_api_key = APIKey(
        **api_key.dict(), 
        user_id=user_id, 
        key_hash=key_hash, 
        key_prefix=key_prefix
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_key(db: Session, api_key_id: UUID, user_id: UUID) -> APIKey:
    return db.query(APIKey).filter(APIKey.id == api_key_id, APIKey.user_id == user_id).first()

def get_api_keys_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[APIKey]:
    return db.query(APIKey).filter(APIKey.user_id == user_id).offset(skip).limit(limit).all()

def delete_api_key(db: Session, api_key_id: UUID, user_id: UUID) -> APIKey:
    db_api_key = get_api_key(db, api_key_id, user_id)
    if not db_api_key:
        return None
        
    db.delete(db_api_key)
    db.commit()
    return db_api_key

