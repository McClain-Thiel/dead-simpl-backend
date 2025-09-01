import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .db.database import init_database
from .routers import auth, bookmark, folders

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.is_development else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    logger.info(f"Starting FastAPI app in {config.environment} environment")
    
    # Initialize database on startup
    await init_database()
    
    yield
    
    logger.info("Shutting down FastAPI app")


app = FastAPI(
    title="AI Pocket Backend",
    description="Backend API for AI Pocket application",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS based on environment
allowed_origins = [
    "http://localhost:8081",  # Local frontend
    "http://localhost:3000",  # Common React dev port
    "http://127.0.0.1:8081",
    "http://127.0.0.1:3000",
]

if config.is_production:
    # Add production origins here
    allowed_origins.extend([
        "https://your-production-domain.com",
    ])
elif config.is_staging:
    # Add staging origins here
    allowed_origins.extend([
        "https://your-staging-domain.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(bookmark.router)
app.include_router(folders.router)
