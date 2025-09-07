from enum import Enum
from typing import Optional, Union, Any, Dict
from pydantic import BaseModel, Field


class FineTuneMethod(str, Enum):
    SFT = "sft"  # Supervised Fine-Tuning
    DPO = "dpo"  # Direct Preference Optimization


class TrainingType(str, Enum):
    FULL = "full"
    LORA = "lora"
    # Add more training types as needed


class LRSchedulerType(str, Enum):
    LINEAR = "linear"
    COSINE = "cosine"
    CONSTANT = "constant"
    # Add more scheduler types as needed


class LRScheduler(BaseModel):
    type: LRSchedulerType = Field(default=LRSchedulerType.LINEAR)
    # Add more scheduler-specific parameters as needed


class TrainingMethod(BaseModel):
    method: FineTuneMethod = Field(default=FineTuneMethod.SFT)
    # Add method-specific parameters as needed


class TrainingTypeConfig(BaseModel):
    type: TrainingType = Field(default=TrainingType.FULL)
    # Add type-specific parameters as needed


class FineTuningJob(BaseModel):
    """Base class for all fine-tuning jobs"""
    training_method: TrainingMethod = Field(default_factory=lambda: TrainingMethod())
    training_type: TrainingTypeConfig = Field(default_factory=lambda: TrainingTypeConfig())


class SFTJob(FineTuningJob):
    """Base class for Supervised Fine-Tuning jobs"""
    training_file: str = Field(..., description="File-ID of a training file")
    model: str = Field(..., description="Name of the base model to run fine-tune job on")
    validation_file: Optional[str] = Field(None, description="File-ID of a validation file")
    n_epochs: int = Field(default=1, description="Number of complete passes through the training dataset")
    learning_rate: float = Field(default=0.00001, description="Controls how quickly the model adapts to new information")
    suffix: Optional[str] = Field(None, description="Suffix that will be added to your fine-tuned model name")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure this is always an SFT job
        self.training_method = TrainingMethod(method=FineTuneMethod.SFT)


class DPOJob(FineTuningJob):
    """Base class for Direct Preference Optimization jobs"""
    training_file: str = Field(..., description="File-ID of a training file")
    model: str = Field(..., description="Name of the base model to run fine-tune job on")
    validation_file: Optional[str] = Field(None, description="File-ID of a validation file")
    n_epochs: int = Field(default=1, description="Number of complete passes through the training dataset")
    learning_rate: float = Field(default=0.00001, description="Controls how quickly the model adapts to new information")
    suffix: Optional[str] = Field(None, description="Suffix that will be added to your fine-tuned model name")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure this is always a DPO job
        self.training_method = TrainingMethod(method=FineTuneMethod.DPO)


class TogetherAISFTJob(SFTJob):
    """Together AI Supervised Fine-Tuning job configuration"""
    n_checkpoints: int = Field(default=1, description="Number of intermediate model versions saved during training")
    n_evals: int = Field(default=0, description="Number of evaluations to be run on validation set during training")
    batch_size: Union[int, str] = Field(default="max", description="Number of training examples processed together")
    lr_scheduler: Optional[LRScheduler] = Field(None, description="The learning rate scheduler to use")
    warmup_ratio: float = Field(default=0, description="Percent of steps to linearly increase learning rate")
    max_grad_norm: float = Field(default=1, description="Max gradient norm for gradient clipping")
    weight_decay: float = Field(default=0, description="Weight decay regularization parameter")
    
    # W&B integration
    wandb_api_key: Optional[str] = Field(None, description="Integration key for W&B platform")
    wandb_base_url: Optional[str] = Field(None, description="Base URL of dedicated W&B instance")
    wandb_project_name: Optional[str] = Field(None, description="W&B project for your run")
    wandb_name: Optional[str] = Field(None, description="W&B name for your run")
    
    # Deprecated/legacy fields
    train_on_inputs: Optional[bool] = Field(None, deprecated=True, description="Whether to mask user messages")
    
    # Checkpoint continuation
    from_checkpoint: Optional[str] = Field(None, description="Checkpoint identifier to continue training from")
    from_hf_model: Optional[str] = Field(None, description="Hugging Face Hub repo to start training from")
    hf_model_revision: Optional[str] = Field(default="main", description="HF Hub model revision")
    hf_api_token: Optional[str] = Field(None, description="API token for Hugging Face Hub")
    hf_output_repo_name: Optional[str] = Field(None, description="HF repository to upload fine-tuned model to")


class TogetherAIDPOJob(DPOJob):
    """Together AI Direct Preference Optimization job configuration"""
    pass


class ClaudeSFTJob(SFTJob):
    """Anthropic Claude Supervised Fine-Tuning job configuration"""
    # Claude-specific parameters (placeholders for now)
    claude_api_key: Optional[str] = Field(None, description="Anthropic API key")
    max_tokens_per_example: Optional[int] = Field(default=8192, description="Maximum tokens per training example")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature for evaluation")
    batch_size: Optional[int] = Field(default=32, description="Training batch size")
    gradient_accumulation_steps: Optional[int] = Field(default=1, description="Gradient accumulation steps")
    evaluation_strategy: Optional[str] = Field(default="epoch", description="When to run evaluation")
    save_steps: Optional[int] = Field(default=500, description="Save checkpoint every N steps")
    logging_steps: Optional[int] = Field(default=100, description="Log metrics every N steps")


class ClaudeDPOJob(DPOJob):
    """Anthropic Claude Direct Preference Optimization job configuration"""
    pass


class OpenAISFTJob(SFTJob):
    """OpenAI Supervised Fine-Tuning job configuration"""
    # OpenAI-specific parameters (placeholders for now) 
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Hyperparameters for fine-tuning")
    integrations: Optional[list] = Field(None, description="Integration configurations")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    
    # OpenAI specific training parameters
    batch_size: Optional[Union[int, str]] = Field(default="auto", description="Batch size for training")
    learning_rate_multiplier: Optional[float] = Field(default=1.0, description="Learning rate multiplier")
    n_epochs: int = Field(default=4, description="Number of epochs (OpenAI default is 4)")


class OpenAIDPOJob(DPOJob):
    """OpenAI Direct Preference Optimization job configuration"""
    pass


# Response models for API endpoints
class FineTuningRun(BaseModel):
    """Base response model for a fine-tuning run"""
    run_id: str
    job_id: str
    status: str
    created_at: str
    progress: Optional[float] = None
    estimated_completion: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class SFTRun(FineTuningRun):
    """Response model for SFT run status"""
    pass

class DPORun(FineTuningRun):
    """Response model for DPO run status"""
    pass

class TogetherAISFTRun(SFTRun):
    """Response model for Together AI SFT run"""
    pass

class ClaudeSFTRun(SFTRun):
    """Response model for Claude SFT run"""
    pass

class OpenAISFTRun(SFTRun):
    """Response model for OpenAI SFT run"""
    pass