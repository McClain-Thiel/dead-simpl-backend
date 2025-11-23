from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLAlchemyEnum, JSON, ARRAY, UUID as SA_UUID, Column
from sqlmodel import Field, SQLModel


class UserRank(str, Enum):
    ADMIN = "admin"
    USER = "user"
    EXPIRED = "expired"
    WAITLIST = "waitlist"


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    firebase_uid: str = Field(unique=True, index=True)
    email: str = Field(index=True)
    name: Optional[str] = None
    rank: UserRank = Field(
        default=UserRank.WAITLIST,
        sa_type=SQLAlchemyEnum(UserRank, name="userrank", create_type=False),
    )
    deleted_at: Optional[datetime] = None


class ScorerType(str, Enum):
    BUILTIN = "builtin"
    LLM_JUDGE = "llm_judge"
    CODE = "code"


class ScorerDefinition(SQLModel, table=True):
    __tablename__ = "scorer_definitions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    scorer_type: ScorerType = Field(
        sa_type=SQLAlchemyEnum(ScorerType, name="scorertype", create_type=False)
    )
    configuration: dict = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationProfile(SQLModel, table=True):
    __tablename__ = "evaluation_profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    scorer_ids: list[UUID] = Field(default_factory=list, sa_column=Column(ARRAY(SA_UUID)))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RunStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvaluationRun(SQLModel, table=True):
    __tablename__ = "evaluation_runs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="evaluation_profiles.id")
    dataset_path: str = Field(max_length=255)
    mlflow_run_id: Optional[str] = Field(default=None, max_length=255)
    status: RunStatus = Field(
        default=RunStatus.PENDING,
        sa_type=SQLAlchemyEnum(RunStatus, name="runstatus", create_type=False)
    )
    summary_results: Optional[dict] = Field(default=None, sa_type=JSON)
    row_details_path: Optional[str] = Field(default=None, max_length=255)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
