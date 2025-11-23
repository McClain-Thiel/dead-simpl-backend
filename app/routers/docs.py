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
        "apiKey": "AIzaSyBD3eDWNqTTShUVwMrKh0mVG1-JFnhICkM",
        "authDomain": "dead-simpl-landing.firebaseapp.com",
        "projectId": "dead-simpl-landing",
        "storageBucket": "dead-simpl-landing.firebasestorage.app",
        "messagingSenderId": "643606161991",
        "appId": "1:643606161991:web:c9305e31acf9d2fe7b9f62",
        "measurementId": "G-YQXCM61EM3"
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
