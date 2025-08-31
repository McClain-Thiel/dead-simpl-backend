from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

import sqlalchemy
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
    deleted_at: Optional[datetime] = None


class Organization(TimestampedModel, table=True):
    __tablename__ = "orgs"
    
    name: str
    slug: str = Field(unique=True, index=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    deleted_at: Optional[datetime] = None
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="organization")
    files: List["File"] = Relationship(back_populates="organization")
    criterion_definitions: List["CriterionDefinition"] = Relationship(back_populates="organization")
    api_keys: List["APIKey"] = Relationship(back_populates="organization")
    operation_events: List["OperationEvent"] = Relationship(back_populates="organization")
    usage_events: List["UsageEvent"] = Relationship(back_populates="organization")
    billing_alerts: List["BillingAlert"] = Relationship(back_populates="organization")
    billing_invoices: List["BillingInvoice"] = Relationship(back_populates="organization")


class Project(TimestampedModel, table=True):
    __tablename__ = "projects"
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    name: str
    description: Optional[str] = None
    deleted_at: Optional[datetime] = None
    
    # Relationships
    organization: Organization = Relationship(back_populates="projects")
    files: List["File"] = Relationship(back_populates="project")
    datasets: List["Dataset"] = Relationship(back_populates="project")
    eval_runs: List["EvalRun"] = Relationship(back_populates="project")
    tune_jobs: List["TuneJob"] = Relationship(back_populates="project")
    models: List["Model"] = Relationship(back_populates="project")
    deployments: List["Deployment"] = Relationship(back_populates="project")
    operation_events: List["OperationEvent"] = Relationship(back_populates="project")
    usage_events: List["UsageEvent"] = Relationship(back_populates="project")


class File(BaseModel, table=True):
    __tablename__ = "files"
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    project_id: Optional[UUID] = Field(foreign_key="projects.id", index=True)
    kind: FileKind
    storage_url: str
    bytes: Optional[int] = None
    sha256: Optional[str] = None
    status: FileStatus = Field(default=FileStatus.PENDING)
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
    # Relationships
    organization: Organization = Relationship(back_populates="files")
    project: Optional[Project] = Relationship(back_populates="files")
    datasets: List["Dataset"] = Relationship(back_populates="file")
    tune_jobs: List["TuneJob"] = Relationship(back_populates="dataset_file")
    model_versions: List["ModelVersion"] = Relationship(back_populates="artifact_file")
    eval_runs: List["EvalRun"] = Relationship(back_populates="report_file")


class Dataset(BaseModel, table=True):
    __tablename__ = "datasets"
    
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    file_id: UUID = Field(foreign_key="files.id")
    name: str
    mode: Mode
    schema: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    rows_estimate: Optional[int] = None
    
    # Relationships
    project: Project = Relationship(back_populates="datasets")
    file: File = Relationship(back_populates="datasets")
    eval_runs: List["EvalRun"] = Relationship(back_populates="dataset")


class CriterionDefinition(BaseModel, table=True):
    __tablename__ = "criterion_definitions"
    __table_args__ = (
        Index("ix_criterion_definitions_org_name", "org_id", "name", unique=True),
    )
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    name: str
    applies_to: CriterionAppliesTo
    method: CriterionMethod
    config: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    
    # Relationships
    organization: Organization = Relationship(back_populates="criterion_definitions")


class EvalRun(BaseModel, table=True):
    __tablename__ = "eval_runs"
    
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    model_ref: str
    dataset_id: UUID = Field(foreign_key="datasets.id")
    eval_type: EvalType = Field(default=EvalType.CRITERIA)
    mode: Mode
    status: JobStatus = Field(default=JobStatus.QUEUED)
    selected_criteria: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    totals: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    token_usage: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    cost_cents: int = Field(default=0)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    report_file_id: Optional[UUID] = Field(foreign_key="files.id")
    
    # Relationships
    project: Project = Relationship(back_populates="eval_runs")
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
    input_json: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    output_json: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    judgments: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_cents: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    eval_run: EvalRun = Relationship(back_populates="row_results")


class TuneJob(BaseModel, table=True):
    __tablename__ = "tune_jobs"
    
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    provider: Provider
    base_model: str
    config: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    dataset_file_id: UUID = Field(foreign_key="files.id")
    provider_job_id: Optional[str] = None
    status: JobStatus = Field(default=JobStatus.QUEUED)
    artifacts: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    metrics: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    cost_cents: int = Field(default=0)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Relationships
    project: Project = Relationship(back_populates="tune_jobs")
    dataset_file: File = Relationship(back_populates="tune_jobs")
    created_models: List["Model"] = Relationship(back_populates="created_from_tune_job")


class Model(BaseModel, table=True):
    __tablename__ = "models"
    
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    name: str
    provider: Provider
    external_model_id: Optional[str] = None
    created_from_tune: Optional[UUID] = Field(foreign_key="tune_jobs.id")
    
    # Relationships
    project: Project = Relationship(back_populates="models")
    created_from_tune_job: Optional[TuneJob] = Relationship(back_populates="models")
    versions: List["ModelVersion"] = Relationship(back_populates="model")


class ModelVersion(BaseModel, table=True):
    __tablename__ = "model_versions"
    
    model_id: UUID = Field(foreign_key="models.id", index=True)
    version: str
    artifact_file_id: Optional[UUID] = Field(foreign_key="files.id")
    card: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
    # Relationships
    model: Model = Relationship(back_populates="versions")
    artifact_file: Optional[File] = Relationship(back_populates="model_versions")
    deployments: List["Deployment"] = Relationship(back_populates="model_version")


class Deployment(BaseModel, table=True):
    __tablename__ = "deployments"
    
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    model_version_id: UUID = Field(foreign_key="model_versions.id")
    status: DeploymentStatus = Field(default=DeploymentStatus.CREATING)
    autoscale: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    config: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    endpoint_slug: str = Field(unique=True, index=True)
    
    # Relationships
    project: Project = Relationship(back_populates="deployments")
    model_version: ModelVersion = Relationship(back_populates="deployments")
    inference_requests: List["InferenceRequest"] = Relationship(back_populates="deployment")


class APIKey(BaseModel, table=True):
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_key_prefix", "key_prefix", unique=True),
    )
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    name: str
    key_prefix: str
    key_hash: str
    scopes: Optional[List[str]] = Field(default=None, sa_type=sqlalchemy.ARRAY(sqlalchemy.String))
    quota: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    status: APIKeyStatus = Field(default=APIKeyStatus.ACTIVE)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Relationships
    organization: Organization = Relationship(back_populates="api_keys")
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
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
    # Relationships
    deployment: Optional[Deployment] = Relationship(back_populates="inference_requests")
    api_key: Optional[APIKey] = Relationship(back_populates="inference_requests")


class OperationEvent(SQLModel, table=True):
    __tablename__ = "operation_events"
    __table_args__ = (
        Index("ix_operation_events_org_occurred", "org_id", "occurred_at"),
        Index("ix_operation_events_project_occurred", "project_id", "occurred_at"),
    )
    
    id: int = Field(primary_key=True)
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    project_id: Optional[UUID] = Field(foreign_key="projects.id", index=True)
    user_id: Optional[UUID] = Field(foreign_key="users.id", index=True)
    source: EventSource
    action: str
    ref_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Organization = Relationship(back_populates="operation_events")
    project: Optional[Project] = Relationship(back_populates="operation_events")


class UsageEvent(SQLModel, table=True):
    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_org_occurred", "org_id", "occurred_at"),
        Index("ix_usage_events_org_project_occurred", "org_id", "project_id", "occurred_at"),
        Index("ix_usage_events_org_metric_occurred", "org_id", "metric", "occurred_at"),
    )
    
    id: int = Field(primary_key=True)
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    project_id: Optional[UUID] = Field(foreign_key="projects.id", index=True)
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
    organization: Organization = Relationship(back_populates="usage_events")
    project: Optional[Project] = Relationship(back_populates="usage_events")


class BillingAlert(BaseModel, table=True):
    __tablename__ = "billing_alerts"
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    threshold_cents: int
    channel: BillingChannel
    target: str
    active: bool = Field(default=True)
    
    # Relationships
    organization: Organization = Relationship(back_populates="billing_alerts")


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
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
    # Relationships
    price_book: PriceBook = Relationship(back_populates="price_items")


class ReconciliationRun(BaseModel, table=True):
    __tablename__ = "reconciliation_runs"
    
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: ReconciliationStatus
    provider: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
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
    payload: Dict[str, Any] = Field(sa_type=sqlalchemy.JSON)
    received_at: datetime = Field(default_factory=datetime.utcnow)


class BillingInvoice(BaseModel, table=True):
    __tablename__ = "billing_invoices"
    __table_args__ = (
        Index("ix_billing_invoices_stripe_id", "stripe_invoice_id", unique=True),
    )
    
    org_id: UUID = Field(foreign_key="orgs.id", index=True)
    stripe_invoice_id: str
    period_start: datetime
    period_end: datetime
    amount_due_cents: int
    currency: str
    status: InvoiceStatus
    hosted_invoice_url: Optional[str] = None
    pdf_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_type=sqlalchemy.JSON)
    
    # Relationships
    organization: Organization = Relationship(back_populates="billing_invoices")


# Optional inference request body sampling table
class InferenceBody(SQLModel, table=True):
    __tablename__ = "inference_bodies"
    
    request_id: UUID = Field(foreign_key="inference_requests.id", primary_key=True)
    prompt_sample: Optional[str] = None
    response_sample: Optional[str] = None