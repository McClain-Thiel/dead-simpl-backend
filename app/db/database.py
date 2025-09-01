"""Database initialization and connection management."""

import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from .models import *  # Import all models to ensure they're registered


class Database:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = None
        
    def init_db(self, database_url: str = None) -> None:
        """Initialize database engine."""
        if database_url is None:
            database_url = os.getenv("SUPABASE_DB_STRING")
            
        if not database_url:
            raise ValueError("SUPABASE_DB_STRING environment variable is required")
            
        self.engine = create_engine(
            database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
    def create_tables(self) -> None:
        """Create all tables if they don't exist."""
        if not self.engine:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        # Create all tables defined in SQLModel metadata
        SQLModel.metadata.create_all(self.engine)
            
    def drop_tables(self) -> None:
        """Drop all tables. Use with caution!"""
        if not self.engine:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        SQLModel.metadata.drop_all(self.engine)
            
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session."""
        if not self.engine:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        with Session(self.engine) as session:
            try:
                yield session
            finally:
                session.close()


# Global database instance
db = Database()


def init_database(database_url: str = None, create_tables: bool = True) -> None:
    """
    Initialize the database connection and optionally create tables.
    
    Args:
        database_url: Database connection URL. If None, uses SUPABASE_DB_STRING env var.
        create_tables: Whether to create tables if they don't exist.
    """
    db.init_db(database_url)
    
    if create_tables:
        db.create_tables()
        print("✓ Database tables created/verified")


def get_db_session() -> Generator[Session, None, None]:
    """Dependency function to get database session for FastAPI."""
    for session in db.get_session():
        yield session