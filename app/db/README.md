# Database Models and Setup

This directory contains the SQLModel-based database models and initialization logic for the ML platform.

## Overview

The database has been restructured to link all entities directly to users, removing the intermediate organization and project layers for simplicity.

## Models

### Core Models
- **User**: Firebase-integrated user accounts with all relationships
- **File**: Raw file uploads (datasets, artifacts, reports)
- **Dataset**: Logical datasets created from CSV files
- **Model**: Model registry entries
- **ModelVersion**: Versioned model artifacts
- **Deployment**: Deployed model endpoints

### Evaluation Models
- **CriterionDefinition**: Custom evaluation criteria per user
- **EvalRun**: Evaluation job tracking
- **EvalRowResult**: Per-row evaluation results

### Training Models
- **TuneJob**: Fine-tuning job tracking

### API & Billing Models
- **APIKey**: User API keys with scopes and quotas
- **InferenceRequest**: Per-request logging and metrics
- **UsageEvent**: Granular billable usage tracking
- **BillingAlert**: Budget notifications
- **BillingInvoice**: Cached invoice metadata

### Audit & Reconciliation
- **OperationEvent**: Audit trail of user actions
- **UserSession**: Active device/session management
- **PriceBook** / **PriceItem**: Pricing catalogs
- **ReconciliationRun** / **ReconciliationAdjustment**: Billing reconciliation
- **StripeWebhookEvent**: Raw Stripe webhook storage

## Database Initialization

The database automatically initializes on FastAPI startup:

```python
from app.db.database import init_database

# Initialize with environment DATABASE_URL
await init_database()

# Or with custom URL
await init_database("postgresql+asyncpg://user:pass@host/db")
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:port/database
# Or for Supabase:
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# Optional
DB_ECHO=true  # Enable SQL query logging
```

## Usage in FastAPI Routes

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db_session
from app.db.models import User, File

async def create_file(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    file = File(
        user_id=current_user.id,
        kind="dataset_csv",
        storage_url="s3://bucket/file.csv"
    )
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file
```

## Key Changes from Original PRD

1. **Removed Organization/Project hierarchy**: All entities now link directly to users
2. **Simplified foreign keys**: `user_id` instead of `org_id`/`project_id`
3. **Updated indexes**: All composite indexes now use `user_id`
4. **Auto-initialization**: Tables are created automatically on startup
5. **Async support**: Full async/await support with AsyncSession

## Relationships

All models maintain proper bidirectional relationships with the User model:

```python
# User has relationships to all owned entities
user.files  # List[File]
user.datasets  # List[Dataset] 
user.models  # List[Model]
user.eval_runs  # List[EvalRun]
# ... etc

# Child models reference back to user
file.user  # User
dataset.user  # User
model.user  # User
# ... etc
```

## Migrations

Use Alembic for database migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "Create tables"

# Apply migration
alembic upgrade head
```

The models will be automatically detected by Alembic when imported.