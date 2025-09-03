from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel, Index


# Enums for various status and type fields
class FileKind(str, Enum):
    DATASET_CSV = "dataset_csv"
    TUNE_JSONL = "tune_jsonl"
    ARTIFACT = "artifact"
    REPORT = "report"


class FileStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    FAILED = "failed"


class Mode(str, Enum):
    CHATBOT = "chatbot"
    RAG = "rag"
    AGENT = "agent"


class CriterionAppliesTo(str, Enum):
    CHATBOT = "chatbot"
    RAG = "rag"
    AGENT = "agent"
    ALL = "all"


class CriterionMethod(str, Enum):
    EXACT_MATCH = "exact_match"
    CONTAINS = "contains"
    PROHIBITED = "prohibited"
    REGEX = "regex"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    JUDGE = "judge"


class EvalType(str, Enum):
    CRITERIA = "criteria"
    ARENA = "arena"
    AB = "ab"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class Provider(str, Enum):
    TOGETHER = "together"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    REGISTRY = "registry"


class DeploymentStatus(str, Enum):
    CREATING = "creating"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    DELETING = "deleting"


class APIKeyStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    REVOKED = "revoked"


class UserRank(str, Enum):
    ADMIN = "admin"
    USER = "user"
    EXPIRED = "expired"
    WAITLIST = "waitlist"


class InferenceRoute(str, Enum):
    CHAT = "/v1/chat"
    COMPLETIONS = "/v1/completions"
    EMBEDDINGS = "/v1/embeddings"
    BATCH = "/v1/batch"


class EventSource(str, Enum):
    CONSOLE = "console"
    WORKER = "worker"
    INFERENCE = "inference"


class UsageSource(str, Enum):
    EVAL = "eval"
    TUNE = "tune"
    DEPLOY = "deploy"


class UsageMetric(str, Enum):
    TOKENS_IN = "tokens_in"
    TOKENS_OUT = "tokens_out"
    JUDGE_TOKENS = "judge_tokens"
    TRAINING_MINUTES = "training_minutes"
    STORAGE_GB_DAY = "storage_gb_day"
    REQUESTS = "requests"


class UsageUnit(str, Enum):
    TOKENS = "tokens"
    MINUTES = "minutes"
    GB_DAY = "gb-day"
    REQUESTS = "requests"


class BillingChannel(str, Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"


class ReconciliationStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"


# Base model for common fields
class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TimestampedModel(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SoftDeletableModel(TimestampedModel):
    deleted_at: Optional[datetime] = None


# Core models
class User(TimestampedModel, table=True):
    __tablename__ = "users"
    
    firebase_uid: str = Field(unique=True, index=True)
    email: str = Field(index=True)
    name: Optional[str] = None
    rank: UserRank = Field(
        default=UserRank.WAITLIST,
        sa_type=SQLAlchemyEnum(UserRank, name="userrank", create_type=False),
    )
    deleted_at: Optional[datetime] = None
    
    # Relationships
    files: List["File"] = Relationship(back_populates="user")
    datasets: List["Dataset"] = Relationship(back_populates="user")
    criterion_definitions: List["CriterionDefinition"] = Relationship(back_populates="user")
    eval_runs: List["EvalRun"] = Relationship(back_populates="user")
    tune_jobs: List["TuneJob"] = Relationship(back_populates="user")
    models: List["Model"] = Relationship(back_populates="user")
    deployments: List["Deployment"] = Relationship(back_populates="user")
    api_keys: List["APIKey"] = Relationship(back_populates="user")
    operation_events: List["OperationEvent"] = Relationship(back_populates="user")
    usage_events: List["UsageEvent"] = Relationship(back_populates="user")
    billing_alerts: List["BillingAlert"] = Relationship(back_populates="user")
    billing_invoices: List["BillingInvoice"] = Relationship(back_populates="user")
    folders: List["Folder"] = Relationship(back_populates="user")
    bookmarks: List["Bookmark"] = Relationship(back_populates="user")


# Organization and Project models removed - linking everything directly to User


class File(BaseModel, table=True):
    __tablename__ = "files"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    kind: FileKind
    storage_url: str
    bytes: Optional[int] = None
    sha256: Optional[str] = None
    status: FileStatus = Field(default=FileStatus.PENDING)
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    user: "User" = Relationship(back_populates="files")
    datasets: List["Dataset"] = Relationship(back_populates="file")
    tune_jobs: List["TuneJob"] = Relationship(back_populates="dataset_file")
    model_versions: List["ModelVersion"] = Relationship(back_populates="artifact_file")
    eval_runs: List["EvalRun"] = Relationship(back_populates="report_file")


class Dataset(BaseModel, table=True):
    __tablename__ = "datasets"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    file_id: UUID = Field(foreign_key="files.id")
    name: str
    mode: Mode
    data_schema: Dict[str, Any] = Field(sa_type=JSON)
    rows_estimate: Optional[int] = None
    
    # Relationships
    user: "User" = Relationship(back_populates="datasets")
    file: File = Relationship(back_populates="datasets")
    eval_runs: List["EvalRun"] = Relationship(back_populates="dataset")


class CriterionDefinition(BaseModel, table=True):
    __tablename__ = "criterion_definitions"
    __table_args__ = (
        Index("ix_criterion_definitions_user_name", "user_id", "name", unique=True),
    )
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    applies_to: CriterionAppliesTo
    method: CriterionMethod
    config: Dict[str, Any] = Field(sa_type=JSON)
    
    # Relationships
    user: "User" = Relationship(back_populates="criterion_definitions")


class EvalRun(BaseModel, table=True):
    __tablename__ = "eval_runs"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    model_ref: str
    dataset_id: UUID = Field(foreign_key="datasets.id")
    eval_type: EvalType = Field(default=EvalType.CRITERIA)
    mode: Mode
    status: JobStatus = Field(default=JobStatus.QUEUED)
    selected_criteria: Dict[str, Any] = Field(sa_type=JSON)
    totals: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    token_usage: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    cost_cents: int = Field(default=0)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    report_file_id: Optional[UUID] = Field(foreign_key="files.id")
    
    # Relationships
    user: "User" = Relationship(back_populates="eval_runs")
    dataset: Dataset = Relationship(back_populates="eval_runs")
    report_file: Optional[File] = Relationship(back_populates="eval_runs")
    row_results: List["EvalRowResult"] = Relationship(back_populates="eval_run")


class EvalRowResult(SQLModel, table=True):
    __tablename__ = "eval_row_results"
    __table_args__ = (
        Index("ix_eval_row_results_run_row", "run_id", "row_index"),
    )
    
    id: int = Field(primary_key=True)
    run_id: UUID = Field(foreign_key="eval_runs.id", index=True)
    row_index: int
    input_json: Dict[str, Any] = Field(sa_type=JSON)
    output_json: Dict[str, Any] = Field(sa_type=JSON)
    judgments: Dict[str, Any] = Field(sa_type=JSON)
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_cents: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    eval_run: EvalRun = Relationship(back_populates="row_results")


class TuneJob(BaseModel, table=True):
    __tablename__ = "tune_jobs"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    provider: Provider
    base_model: str
    config: Dict[str, Any] = Field(sa_type=JSON)
    dataset_file_id: UUID = Field(foreign_key="files.id")
    provider_job_id: Optional[str] = None
    status: JobStatus = Field(default=JobStatus.QUEUED)
    artifacts: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    metrics: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    cost_cents: int = Field(default=0)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Relationships
    user: "User" = Relationship(back_populates="tune_jobs")
    dataset_file: File = Relationship(back_populates="tune_jobs")
    created_models: List["Model"] = Relationship(back_populates="created_from_tune_job")


class Model(BaseModel, table=True):
    __tablename__ = "models"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    provider: Provider
    external_model_id: Optional[str] = None
    created_from_tune: Optional[UUID] = Field(foreign_key="tune_jobs.id")
    
    # Relationships
    user: "User" = Relationship(back_populates="models")
    created_from_tune_job: Optional[TuneJob] = Relationship(back_populates="created_models")
    versions: List["ModelVersion"] = Relationship(back_populates="model")


class ModelVersion(BaseModel, table=True):
    __tablename__ = "model_versions"
    
    model_id: UUID = Field(foreign_key="models.id", index=True)
    version: str
    artifact_file_id: Optional[UUID] = Field(foreign_key="files.id")
    card: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    model: Model = Relationship(back_populates="versions")
    artifact_file: Optional[File] = Relationship(back_populates="model_versions")
    deployments: List["Deployment"] = Relationship(back_populates="model_version")


class Deployment(BaseModel, table=True):
    __tablename__ = "deployments"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    model_version_id: UUID = Field(foreign_key="model_versions.id")
    status: DeploymentStatus = Field(default=DeploymentStatus.CREATING)
    autoscale: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    config: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    endpoint_slug: str = Field(unique=True, index=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="deployments")
    model_version: ModelVersion = Relationship(back_populates="deployments")
    inference_requests: List["InferenceRequest"] = Relationship(back_populates="deployment")


class APIKey(BaseModel, table=True):
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_key_prefix", "key_prefix", unique=True),
    )
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    key_prefix: str
    key_hash: str
    scopes: Optional[List[str]] = Field(default=None, sa_type=ARRAY(String))
    quota: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    status: APIKeyStatus = Field(default=APIKeyStatus.ACTIVE)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Relationships
    user: "User" = Relationship(back_populates="api_keys")
    inference_requests: List["InferenceRequest"] = Relationship(back_populates="api_key")


class InferenceRequest(BaseModel, table=True):
    __tablename__ = "inference_requests"
    __table_args__ = (
        Index("ix_inference_requests_deployment_created", "deployment_id", "created_at"),
        Index("ix_inference_requests_api_key_created", "api_key_id", "created_at"),
    )
    
    deployment_id: Optional[UUID] = Field(foreign_key="deployments.id", index=True)
    api_key_id: Optional[UUID] = Field(foreign_key="api_keys.id", index=True)
    model_ref: str
    route: InferenceRoute
    status_code: int
    error_code: Optional[str] = None
    latency_ms: Optional[int] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_cents: Optional[int] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    deployment: Optional[Deployment] = Relationship(back_populates="inference_requests")
    api_key: Optional[APIKey] = Relationship(back_populates="inference_requests")


class OperationEvent(SQLModel, table=True):
    __tablename__ = "operation_events"
    __table_args__ = (
        Index("ix_operation_events_user_occurred", "user_id", "occurred_at"),
    )
    
    id: int = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    source: EventSource
    action: str
    ref_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="operation_events")


class UsageEvent(SQLModel, table=True):
    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_user_occurred", "user_id", "occurred_at"),
        Index("ix_usage_events_user_metric_occurred", "user_id", "metric", "occurred_at"),
    )
    
    id: int = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    source: UsageSource
    ref_id: Optional[str] = None
    metric: UsageMetric
    quantity: int
    unit: UsageUnit
    cost_cents: int
    stripe_invoice_item_id: Optional[str] = None
    reconciled_at: Optional[datetime] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="usage_events")


class BillingAlert(BaseModel, table=True):
    __tablename__ = "billing_alerts"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    threshold_cents: int
    channel: BillingChannel
    target: str
    active: bool = Field(default=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="billing_alerts")


class UserSession(BaseModel, table=True):
    __tablename__ = "user_sessions"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    device_label: Optional[str] = None
    ip_hash: Optional[str] = None
    user_agent_hash: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


class PriceBook(BaseModel, table=True):
    __tablename__ = "price_books"
    
    name: str
    valid_from: datetime
    valid_to: Optional[datetime] = None
    
    # Relationships
    price_items: List["PriceItem"] = Relationship(back_populates="price_book")


class PriceItem(BaseModel, table=True):
    __tablename__ = "price_items"
    
    price_book_id: UUID = Field(foreign_key="price_books.id", index=True)
    provider: str
    model: str
    metric: str
    unit: str
    price_per_unit_micros: int
    currency: str = Field(default="usd")
    effective_from: datetime
    effective_to: Optional[datetime] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    price_book: PriceBook = Relationship(back_populates="price_items")


class ReconciliationRun(BaseModel, table=True):
    __tablename__ = "reconciliation_runs"
    
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: ReconciliationStatus
    provider: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    adjustments: List["ReconciliationAdjustment"] = Relationship(back_populates="reconciliation_run")


class ReconciliationAdjustment(BaseModel, table=True):
    __tablename__ = "reconciliation_adjustments"
    
    run_id: UUID = Field(foreign_key="reconciliation_runs.id", index=True)
    usage_event_id: Optional[int] = Field(foreign_key="usage_events.id", index=True)
    delta_cost_cents: int
    reason: str
    
    # Relationships
    reconciliation_run: ReconciliationRun = Relationship(back_populates="adjustments")


class StripeWebhookEvent(BaseModel, table=True):
    __tablename__ = "stripe_webhook_events"
    
    type: str
    payload: Dict[str, Any] = Field(sa_type=JSON)
    received_at: datetime = Field(default_factory=datetime.utcnow)


class BillingInvoice(BaseModel, table=True):
    __tablename__ = "billing_invoices"
    __table_args__ = (
        Index("ix_billing_invoices_stripe_id", "stripe_invoice_id", unique=True),
    )
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    stripe_invoice_id: str
    period_start: datetime
    period_end: datetime
    amount_due_cents: int
    currency: str
    status: InvoiceStatus
    hosted_invoice_url: Optional[str] = None
    pdf_url: Optional[str] = None
    invoice_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    
    # Relationships
    user: "User" = Relationship(back_populates="billing_invoices")


# Optional inference request body sampling table
class InferenceBody(SQLModel, table=True):
    __tablename__ = "inference_bodies"
    
    request_id: UUID = Field(foreign_key="inference_requests.id", primary_key=True)
    prompt_sample: Optional[str] = None
    response_sample: Optional[str] = None


# Simple models for bookmark functionality (for compatibility)
class Folder(BaseModel, table=True):
    __tablename__ = "folders"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = Field(foreign_key="folders.id", default=None)
    
    # Relationships
    user: "User" = Relationship(back_populates="folders")
    bookmarks: List["Bookmark"] = Relationship(back_populates="folder")
    children: List["Folder"] = Relationship(back_populates="parent")
    parent: Optional["Folder"] = Relationship(back_populates="children",
        sa_relationship_kwargs={"remote_side": "Folder.id"})


class Bookmark(BaseModel, table=True):
    __tablename__ = "bookmarks"
    
    user_id: UUID = Field(foreign_key="users.id", index=True)
    folder_id: Optional[UUID] = Field(foreign_key="folders.id", default=None)
    title: str
    url: str
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_type=ARRAY(String))
    
    # Relationships
    user: "User" = Relationship(back_populates="bookmarks")
    folder: Optional[Folder] = Relationship(back_populates="bookmarks")