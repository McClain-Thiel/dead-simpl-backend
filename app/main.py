import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth as firebase_auth
from sqlmodel import select

from .db.database import init_database, db
from .db.models import User, UserRank
from .middleware.security import SecurityHeadersMiddleware
from .routers import auth, docs, eval

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_database()
    logger.info("✓ Database initialized successfully")
    
    # Seed Admin User
    try:
        admin_email = "mcclain@dead-simpl.com"
        # Check if user exists in Firebase
        try:
            fb_user = firebase_auth.get_user_by_email(admin_email)
            # Check if user exists in DB
            with next(db.get_session()) as session:
                user = session.exec(select(User).where(User.email == admin_email)).first()
                if not user:
                    logger.info(f"Seeding admin user {admin_email}")
                    user = User(
                        firebase_uid=fb_user.uid,
                        email=admin_email,
                        rank=UserRank.ADMIN
                    )
                    session.add(user)
                    session.commit()
                    logger.info("✓ Admin user seeded")
                elif user.rank != UserRank.ADMIN:
                    logger.info(f"Promoting user {admin_email} to admin")
                    user.rank = UserRank.ADMIN
                    session.add(user)
                    session.commit()
                    logger.info("✓ User promoted to admin")
        except firebase_auth.UserNotFoundError:
            logger.warning(f"Admin user {admin_email} not found in Firebase, skipping seed")
        except ValueError as e:
             # Firebase not initialized
             logger.warning(f"Firebase not initialized, skipping admin seed: {e}")

    except Exception as e:
        logger.error(f"Error seeding admin user: {e}")

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
app.include_router(docs.router)
app.include_router(eval.router, prefix="/api")
