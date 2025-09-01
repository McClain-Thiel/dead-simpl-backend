"""Database initialization and migration utilities."""
import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlmodel import SQLModel

from ..config import config

logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations to ensure database is up to date."""
    try:
        logger.info(f"Running migrations for {config.environment} environment...")
        
        # Configure Alembic
        alembic_cfg = AlembicConfig("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", config.database_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise


def create_tables():
    """Create all tables (fallback if migrations fail)."""
    try:
        logger.info("Creating tables...")
        from ..dependencies import engine
        SQLModel.metadata.create_all(engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


async def init_database():
    """Initialize database on application startup."""
    logger.info(f"Initializing database for {config.environment} environment")
    
    try:
        # Try to run migrations first
        run_migrations()
    except Exception as e:
        logger.warning(f"Migration failed: {e}. Falling back to table creation.")
        try:
            create_tables()
        except Exception as create_error:
            logger.error(f"Failed to create tables: {create_error}")
            raise
    
    logger.info("Database initialization completed")