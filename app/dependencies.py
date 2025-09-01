import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, create_engine, select
from supabase import Client, create_client

from .config import config
from .db.models import User

logger = logging.getLogger(__name__)

# Supabase connection (for authentication)
url = config.supabase_url
key = config.supabase_key

# Database connection (environment-aware)
engine = create_engine(config.database_url, echo=config.is_development)


def get_supabase_client() -> Client:
    logger.info("Initializing Supabase client")
    return create_client(url, key)


SupabaseDependency = Annotated[Client, Depends(get_supabase_client)]


def get_db_session():
    with Session(engine) as session:
        yield session


DBSessionDependency = Annotated[Session, Depends(get_db_session)]

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="token")
AccessTokenDependency = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
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

    user = db.exec(select(User).where(User.id == response.user.id)).first()

    if not user:
        logger.error("User not found in the database")
        raise HTTPException(status_code=404, detail="User not found")

    return user


UserDependency = Annotated[User, Depends(get_current_user)]
