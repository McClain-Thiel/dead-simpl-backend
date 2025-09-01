import logging
import os
import secrets
import time
from typing import Optional, Dict
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from ..dependencies import UserDependency, get_current_user, DBSessionDependency, SupabaseDependency

logger = logging.getLogger(__name__)

router = APIRouter()

# Session store with expiration (24 hours)
# In production, use Redis or database sessions
docs_sessions: Dict[str, Dict[str, any]] = {}

# Rate limiting for login attempts (simple in-memory approach)
# In production, use Redis or more sophisticated rate limiting
login_attempts: Dict[str, list] = defaultdict(list)

# Environment-based admin users (for additional security)
DOCS_ADMIN_EMAILS = os.environ.get("DOCS_ADMIN_EMAILS", "").split(",")
DOCS_ADMIN_EMAILS = [email.strip() for email in DOCS_ADMIN_EMAILS if email.strip()]

@router.get("/docs-login", response_class=HTMLResponse)
async def docs_login_page():
    """Serve a simple login page for docs access"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Documentation Access</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 100px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .login-container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h2 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: bold;
            }
            input[type="email"], input[type="password"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            .error {
                color: #dc3545;
                margin-top: 10px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Documentation Access</h2>
            <form action="/docs-auth" method="post">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Access Documentation</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/docs-auth")
async def authenticate_for_docs(
    request: Request,
    supabase: SupabaseDependency,
    db: DBSessionDependency,
    email: str = Form(...),
    password: str = Form(...)
):
    """Authenticate user for docs access"""
    client_ip = request.client.host
    
    # Check rate limiting
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rate Limited</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 400px;
                    margin: 100px auto;
                    padding: 20px;
                    text-align: center;
                    background-color: #f5f5f5;
                }
                .error-container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .error {
                    color: #dc3545;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2 class="error">Rate Limited</h2>
                <p>Too many login attempts. Please try again in 15 minutes.</p>
                <p><a href="/docs-login">Back to login</a></p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=429)
    
    # Record this login attempt
    record_login_attempt(client_ip)
    
    try:
        # Validate environment variables
        if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
            logger.error("Supabase configuration missing")
            raise HTTPException(status_code=500, detail="Authentication service not configured")
        
        # Use Supabase to authenticate the user
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        
        # Additional check: if admin emails are configured, only allow those users
        if DOCS_ADMIN_EMAILS and email not in DOCS_ADMIN_EMAILS:
            logger.warning(f"Non-admin user {email} attempted to access docs")
            raise Exception("Access denied: Admin privileges required")
        
        # Generate secure session ID and store session data
        session_id = secrets.token_urlsafe(32)
        docs_sessions[session_id] = {
            "user_id": response.user.id,
            "email": email,
            "created_at": time.time(),
            "is_admin": email in DOCS_ADMIN_EMAILS if DOCS_ADMIN_EMAILS else True
        }
        
        logger.info(f"User {email} successfully authenticated for docs access")
        
        # Clean up expired sessions periodically
        cleanup_expired_sessions()
        
        # Set a cookie and redirect to docs
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting...</title>
                <script>
                    document.cookie = "docs_session={session_id}; path=/; secure; samesite=strict";
                    window.location.href = "/docs";
                </script>
            </head>
            <body>
                <p>Authentication successful. Redirecting to documentation...</p>
                <p>If not redirected automatically, <a href="/docs">click here</a>.</p>
            </body>
            </html>
            """
        
        html_response = HTMLResponse(content=html_content, status_code=200)
        html_response.set_cookie(
            key="docs_session",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
            max_age=86400  # 24 hours
        )
        
        # Add security headers
        html_response.headers["X-Content-Type-Options"] = "nosniff"
        html_response.headers["X-Frame-Options"] = "DENY"
        html_response.headers["X-XSS-Protection"] = "1; mode=block"
        return html_response
        
    except Exception as e:
        logger.error("Error during docs authentication: %s", e)
        # Return to login page with error
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Documentation Access</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 400px;
                    margin: 100px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .login-container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h2 {
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    color: #555;
                    font-weight: bold;
                }
                input[type="email"], input[type="password"] {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                    font-size: 16px;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .error {
                    color: #dc3545;
                    margin-top: 10px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>Documentation Access</h2>
                <form action="/docs-auth" method="post">
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Access Documentation</button>
                </form>
                <div class="error">Invalid credentials. Please try again.</div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=401)

def check_docs_session(request: Request) -> bool:
    """Check if user has valid docs session"""
    session_cookie = request.cookies.get("docs_session")
    if not session_cookie or session_cookie not in docs_sessions:
        return False
    
    # Check if session has expired (24 hours)
    session_data = docs_sessions[session_cookie]
    if time.time() - session_data["created_at"] > 86400:  # 24 hours
        del docs_sessions[session_cookie]
        return False
    
    return True

def cleanup_expired_sessions():
    """Remove expired sessions"""
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, data in docs_sessions.items()
        if current_time - data["created_at"] > 86400
    ]
    for session_id in expired_sessions:
        del docs_sessions[session_id]

def check_rate_limit(client_ip: str) -> bool:
    """Check if client IP is rate limited (max 5 attempts per 15 minutes)"""
    current_time = time.time()
    attempts = login_attempts[client_ip]
    
    # Remove attempts older than 15 minutes
    login_attempts[client_ip] = [
        attempt_time for attempt_time in attempts
        if current_time - attempt_time < 900  # 15 minutes
    ]
    
    return len(login_attempts[client_ip]) < 5

def record_login_attempt(client_ip: str):
    """Record a login attempt for rate limiting"""
    login_attempts[client_ip].append(time.time())

@router.get("/docs", response_class=HTMLResponse)
async def get_documentation(request: Request):
    """Protected Swagger UI documentation"""
    if not check_docs_session(request):
        # Redirect to login page
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Required</title>
            <script>
                window.location.href = "/docs-login";
            </script>
        </head>
        <body>
            <p>Authentication required. Redirecting to login...</p>
            <p>If not redirected automatically, <a href="/docs-login">click here</a>.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=401)
    
    # Get session data to show user info
    session_cookie = request.cookies.get("docs_session")
    session_data = docs_sessions.get(session_cookie, {})
    user_email = session_data.get("email", "Unknown")
    
    swagger_html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )
    
    # Add logout button to the Swagger UI
    logout_script = f"""
    <style>
        .logout-container {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            z-index: 9999;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}
        .logout-btn {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            margin-left: 10px;
        }}
        .logout-btn:hover {{
            background: #c82333;
        }}
    </style>
    <div class="logout-container">
        Logged in as: {user_email}
        <form method="post" action="/docs-logout" style="display: inline;">
            <button type="submit" class="logout-btn">Logout</button>
        </form>
    </div>
    """
    
    # Insert the logout UI into the Swagger HTML
    modified_html = swagger_html.body.decode('utf-8').replace(
        '</body>',
        f'{logout_script}</body>'
    )
    
    return HTMLResponse(content=modified_html)

@router.get("/redoc", response_class=HTMLResponse)
async def get_redoc_documentation(request: Request):
    """Protected ReDoc documentation"""
    if not check_docs_session(request):
        # Redirect to login page
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Required</title>
            <script>
                window.location.href = "/docs-login";
            </script>
        </head>
        <body>
            <p>Authentication required. Redirecting to login...</p>
            <p>If not redirected automatically, <a href="/docs-login">click here</a>.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=401)
    
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="API Documentation",
    )

@router.get("/openapi.json")
async def get_openapi_json(request: Request):
    """Protected OpenAPI JSON schema"""
    if not check_docs_session(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get the main app instance to generate OpenAPI schema
    from ..main import app
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

@router.post("/docs-logout")
async def logout_from_docs(request: Request):
    """Logout from docs session"""
    session_cookie = request.cookies.get("docs_session")
    if session_cookie and session_cookie in docs_sessions:
        del docs_sessions[session_cookie]
    
    html_response = HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Logged Out</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 400px;
                    margin: 100px auto;
                    padding: 20px;
                    text-align: center;
                    background-color: #f5f5f5;
                }
                .message-container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <h2>Logged Out</h2>
                <p>You have been successfully logged out from the documentation.</p>
                <p><a href="/docs-login">Login again</a></p>
            </div>
        </body>
        </html>
        """,
        status_code=200
    )
    html_response.delete_cookie(key="docs_session", path="/")
    return html_response