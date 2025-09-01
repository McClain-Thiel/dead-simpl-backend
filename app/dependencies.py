import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from supabase import Client, create_client

from .db.database import get_db_session
from .db.models import User

logger = logging.getLogger(__name__)

load_dotenv()

# Supabase connection
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")


def get_supabase_client() -> Client:
    logger.info("Initializing Supabase client")
    return create_client(url, key)


SupabaseDependency = Annotated[Client, Depends(get_supabase_client)]
DBSessionDependency = Annotated[Session, Depends(get_db_session)]

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="token")
AccessTokenDependency = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(
    access_token: AccessTokenDependency,
    db: DBSessionDependency,
    supabase_client: Client = Depends(get_supabase_client),
) -> User:
    """Get current user from access_token and validate at the same time"""
    try:
        response = supabase_client.auth.get_user(access_token)
    except Exception as e:
        logger.error("Error during getting user %s", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    # Use firebase_uid instead of id for lookup since we removed the auth.users reference
    result = db.exec(select(User).where(User.firebase_uid == response.user.id))
    user = result.first()

    if not user:
        logger.error("User not found in the database")
        raise HTTPException(status_code=404, detail="Invalid token")

    return user


UserDependency = Annotated[User, Depends(get_current_user)]
