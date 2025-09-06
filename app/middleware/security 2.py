"""Security middleware for adding security headers and other protections."""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header for HTTPS (will be ignored on HTTP)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Log access to sensitive endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/docs-auth"]:
            client_ip = request.client.host
            user_agent = request.headers.get("user-agent", "Unknown")
            logger.info(f"Access to {request.url.path} from {client_ip} - {user_agent}")
        
        return response