import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..db.models import User
from ..dependencies import DBSessionDependency
from ..schemas.auth import UserSign, Token
from firebase_admin import auth

logger = logging.getLogger(__name__)

router = APIRouter()





@router.post("/sign_up/", tags=["users"])
def sign_up(user: UserSign, db: DBSessionDependency):
    try:
        firebase_user = auth.create_user(
            email=user.email,
            password=user.password
        )
    except Exception as e:
        logger.error("Error during signup %s", e)
        raise HTTPException(status_code=400, detail="Error during signup")

    # Create an User in our database
    db_user = User(firebase_uid=firebase_user.uid, email=user.email)
    logger.warning("Mail verification is not checked !")
    try:
        db.add(db_user)
        db.commit()
    except Exception as e:
        logger.error("Error during user creation %s", e)
        raise HTTPException(status_code=400, detail="Error during user creation")

    return {"message": "User signed up successfully, waiting for confirmation."}


@router.post("/sign_in/", tags=["users"])
def sign_in(user: UserSign):
    try:
        firebase_user = auth.get_user_by_email(user.email)
        # This is not a real sign-in, as we are not verifying the password.
        # We are just getting the user from Firebase and then creating a custom token.
        # The custom token can be used by the client to sign in to Firebase.
        custom_token = auth.create_custom_token(firebase_user.uid)
        return {"token": custom_token}
    except Exception as e:
        logger.error("Error during signin %s", e)
        raise HTTPException(status_code=400, detail="Error during signin")


@router.post("/docs-login", include_in_schema=False)
def docs_login(token: Token, response: Response):
    response.set_cookie(
        key="access_token",
        value=token.id_token,
        httponly=True,
        samesite="lax",
        secure=False, # Set to true in production
        path="/",
    )
    return {"status": "ok"}
