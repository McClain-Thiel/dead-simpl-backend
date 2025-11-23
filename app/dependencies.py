import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
from sqlmodel import Session, select

from .db.database import get_db_session
from .db.models import User
from . import firebase_config
from firebase_admin import auth

logger = logging.getLogger(__name__)

DBSessionDependency = Annotated[Session, Depends(get_db_session)]

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)
AccessTokenDependency = Annotated[str | None, Depends(cookie_scheme)]


def get_current_user(
    token: AccessTokenDependency,
    db: DBSessionDependency,
) -> User | None:
    """Get current user from access_token and validate at the same time"""
    if not token:
        return None
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
    except Exception as e:
        logger.error("Error during getting user %s", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    result = db.exec(select(User).where(User.firebase_uid == uid))
    user = result.first()

    if not user:
        logger.error("User not found in the database")
        return None

    return user


UserDependency = Annotated[User | None, Depends(get_current_user)]