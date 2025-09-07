import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_database
from .middleware.security import SecurityHeadersMiddleware
from .routers import auth, docs, fine_tuning, deployments, api_keys, files, evals, stripe

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
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8081",
        "https://portal.dead-simpl.com",
        "https://dead-simpl.com",
        "https://www.dead-simpl.com"
    ],
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
app.include_router(docs.router)
app.include_router(fine_tuning.router)
app.include_router(deployments.router)
app.include_router(api_keys.router)
app.include_router(files.router)
app.include_router(evals.router)
app.include_router(stripe.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Test comment for CI/CD
# Another test comment
