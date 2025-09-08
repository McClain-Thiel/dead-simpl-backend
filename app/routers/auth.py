import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Response, Header
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin import auth
from typing import Optional

from ..db.models import User, UserRank
from ..dependencies import DBSessionDependency
from ..schemas.auth import UserSign, Token

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


def _get_roles_and_permissions_for_rank(rank: UserRank):
    """Map user ranks to roles and permissions."""
    role_permissions_map = {
        UserRank.ADMIN: {
            "roles": [
                {
                    "id": "role-admin", 
                    "name": "admin",
                    "permissions": ["deploy", "manage_users", "delete_models", "tune_models", "evaluate_models"]
                }
            ],
            "permissions": ["deploy", "manage_users", "delete_models", "tune_models", "evaluate_models"]
        },
        UserRank.USER: {
            "roles": [
                {
                    "id": "role-user",
                    "name": "data_scientist", 
                    "permissions": ["tune_models", "evaluate_models"]
                }
            ],
            "permissions": ["tune_models", "evaluate_models"]
        },
        UserRank.EXPIRED: {
            "roles": [],
            "permissions": []
        },
        UserRank.WAITLIST: {
            "roles": [],
            "permissions": []
        }
    }
    
    return role_permissions_map.get(rank, {"roles": [], "permissions": []})


@router.get("/api/verify-user", tags=["auth"])
def verify_user(
    db: DBSessionDependency,
    authorization: Optional[str] = Header(None),
):
    """Verify Firebase ID token and return user info with roles and permissions."""
    
    # Check for Authorization header
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token"
        )
    
    # Extract token from Bearer format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token['uid']
        
        # Get additional user info from Firebase token
        firebase_email = decoded_token.get('email', '')
        firebase_name = decoded_token.get('name', '')
        firebase_photo = decoded_token.get('picture', '')
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"  
        )
    except Exception as e:
        logger.error("Error during token verification: %s", e)
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    # Find user in our database
    from sqlmodel import select
    result = db.exec(select(User).where(User.firebase_uid == firebase_uid))
    user = result.first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found in system"
        )
    
    # Check if user is authorized (not expired or waitlisted)  
    if user.rank in [UserRank.EXPIRED, UserRank.WAITLIST]:
        raise HTTPException(
            status_code=403,
            detail="User not found or not authorized"
        )
    
    # Get roles and permissions based on user rank
    roles_permissions = _get_roles_and_permissions_for_rank(user.rank)
    
    return {
        "authorized": True,
        "user": {
            "id": str(user.id),
            "email": firebase_email or user.email,
            "displayName": firebase_name or user.name or "",
            "photoURL": firebase_photo or "",
            "roles": roles_permissions["roles"],
            "permissions": roles_permissions["permissions"]
        }
    }
