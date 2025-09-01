import os
from typing import Literal

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

Environment = Literal["development", "staging", "production"]


class Config:
    """Application configuration based on environment."""
    
    def __init__(self):
        self.environment: Environment = os.getenv("ENVIRONMENT", "development")
        
        # Supabase configuration (always needed for auth)
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Database configuration
        self.database_url = self._get_database_url()
        
        # Development specific
        self.dev_env = os.getenv("DEV_ENV", "dev" if self.environment == "development" else "prod")
        
    def _get_database_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        if self.environment == "development":
            # For local development, use local PostgreSQL
            host = os.getenv("LOCAL_DB_HOST", "localhost")
            port = os.getenv("LOCAL_DB_PORT", "5432")
            db_name = os.getenv("LOCAL_DB_NAME", "aipocket_local")
            user = os.getenv("LOCAL_DB_USER", "postgres")
            password = os.getenv("LOCAL_DB_PASSWORD", "postgres")
            return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        else:
            # For staging and production, use Supabase
            return os.getenv("SUPABASE_DB_STRING")
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# Global config instance
config = Config()