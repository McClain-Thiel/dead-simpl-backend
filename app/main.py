import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_database
from .middleware.security import SecurityHeadersMiddleware
from .routers import auth, bookmark, folders, docs

# Load environment variables first
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_database()
    logger.info("✓ Database initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize database: {e}")
    # Don't raise - allow the app to start even if database is not available
    logger.warning("Application starting without database connection")

app = FastAPI(
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None  # Disable default openapi.json
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Allow only this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include routers
app.include_router(auth.router)
app.include_router(bookmark.router)
app.include_router(folders.router)
app.include_router(docs.router)
