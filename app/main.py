import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_database

logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_database()
    logger.info("✓ Database initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize database: {e}")
    raise

app = FastAPI()

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

# Add routers here as needed
# app.include_router(your_router)
