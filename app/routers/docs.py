import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from ..dependencies import UserDependency, get_current_user
from ..db.models import User, UserRank

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/docs/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(content=open("app/static/login.html").read())


@router.get("/docs/config")
async def get_firebase_config():
    return JSONResponse({
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.environ.get("FIREBASE_APP_ID"),
        "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
    })


@router.get("/docs", response_class=HTMLResponse)
async def get_documentation(user: UserDependency):
    if not user:
        return RedirectResponse(url="/docs/login")
    if user.rank != UserRank.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )


@router.get("/redoc", response_class=HTMLResponse)
async def get_redoc_documentation(user: UserDependency):
    if not user:
        return RedirectResponse(url="/docs/login")
    if user.rank != UserRank.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    return get_redoc_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )


@router.get("/openapi.json")
async def get_openapi_json(user: UserDependency):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.rank != UserRank.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    from ..main import app
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
