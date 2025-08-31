"""Database initialization and connection management."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from .models import *  # Import all models to ensure they're registered


class Database:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        
    def init_db(self, database_url: str = None) -> None:
        """Initialize database engine and session maker."""
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")
            
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        # Convert postgres:// to postgresql+asyncpg:// for async support
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        self.engine = create_async_engine(
            database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            future=True
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    async def create_tables(self) -> None:
        """Create all tables if they don't exist."""
        if not self.engine:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        async with self.engine.begin() as conn:
            # Create all tables defined in SQLModel metadata
            await conn.run_sync(SQLModel.metadata.create_all)
            
    async def drop_tables(self) -> None:
        """Drop all tables. Use with caution!"""
        if not self.engine:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.session_maker:
            raise ValueError("Database not initialized. Call init_db() first.")
            
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
                
    async def close(self) -> None:
        """Close database engine."""
        if self.engine:
            await self.engine.dispose()


# Global database instance
db = Database()


async def init_database(database_url: str = None, create_tables: bool = True) -> None:
    """
    Initialize the database connection and optionally create tables.
    
    Args:
        database_url: Database connection URL. If None, uses DATABASE_URL env var.
        create_tables: Whether to create tables if they don't exist.
    """
    db.init_db(database_url)
    
    if create_tables:
        await db.create_tables()
        print("✓ Database tables created/verified")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get database session for FastAPI."""
    async for session in db.get_session():
        yield session


async def close_database() -> None:
    """Close database connections."""
    await db.close()