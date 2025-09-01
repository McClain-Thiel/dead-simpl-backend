#!/usr/bin/env python3
"""Test script to verify environment configuration."""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_environment_config():
    """Test that environment configuration works correctly."""
    
    print("🧪 Testing environment configuration...\n")
    
    # Test different environment configurations
    environments = ["development", "staging", "production"]
    
    for env in environments:
        print(f"Testing {env} environment:")
        
        # Set environment
        os.environ["ENVIRONMENT"] = env
        
        # Import config (this will reload with new environment)
        if "app.config" in sys.modules:
            del sys.modules["app.config"]
        
        from app.config import config
        
        print(f"  ✅ Environment: {config.environment}")
        print(f"  ✅ Database URL: {config.database_url}")
        print(f"  ✅ Is Development: {config.is_development}")
        print(f"  ✅ Is Staging: {config.is_staging}")
        print(f"  ✅ Is Production: {config.is_production}")
        print()

def test_database_connection():
    """Test database connection for current environment."""
    
    print("🔌 Testing database connection...\n")
    
    try:
        from app.dependencies import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  ✅ Database connection successful!")
            print(f"  ✅ PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        print("  💡 Make sure your database is running and .env file is configured correctly")

def main():
    """Run all tests."""
    
    print("🚀 AI Pocket Backend - Environment Test\\n")
    print("=" * 50)
    
    test_environment_config()
    
    print("=" * 50)
    test_database_connection()
    
    print("=" * 50)
    print("✅ Environment test completed!")

if __name__ == "__main__":
    main()