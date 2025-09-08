import secrets
import hashlib
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import DBSessionDependency, get_current_user
from ..db.models import APIKey, User
from ..schemas.api_key import APIKey as APIKeySchema, APIKeyCreate, APIKeyWithSecret
from ..db import crud

router = APIRouter(
    prefix="/api/api-keys",
    tags=["API Keys"],
    dependencies=[Depends(get_current_user)]
)

def generate_api_key():
    return "sk_dead_" + secrets.token_urlsafe(32)

def hash_api_key(api_key: str):
    return hashlib.sha256(api_key.encode()).hexdigest()

@router.post("/", response_model=APIKeyWithSecret)
def create_api_key(api_key: APIKeyCreate, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Create a new API key."""
    key_secret = generate_api_key()
    key_hash = hash_api_key(key_secret)
    key_prefix = key_secret[-4:]
    
    db_api_key = crud.create_api_key(
        db=db, 
        api_key=api_key, 
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix
    )

    return APIKeyWithSecret(
        **db_api_key.__dict__,
        key_secret=key_secret
    )

@router.get("/", response_model=List[APIKeySchema])
def read_api_keys(db: DBSessionDependency, user: User = Depends(get_current_user), skip: int = 0, limit: int = 100):
    """Retrieve API keys for the current user."""
    api_keys = crud.get_api_keys_by_user(db=db, user_id=user.id, skip=skip, limit=limit)
    return api_keys

@router.delete("/{api_key_id}", response_model=APIKeySchema)
def delete_api_key(api_key_id: UUID, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Delete an API key."""
    db_api_key = crud.delete_api_key(db=db, api_key_id=api_key_id, user_id=user.id)
    if db_api_key is None:
        raise HTTPException(status_code=404, detail="API Key not found")
    return db_api_key 