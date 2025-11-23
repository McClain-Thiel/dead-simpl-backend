import importlib
from typing import Any, Dict, List

from mlflow.metrics.genai import EvaluationExample, make_genai_metric

from app.db.models import ScorerDefinition, ScorerType


def scorer_factory(scorer_def: ScorerDefinition) -> Any:
    """
    Hydrates a DB record into an MLflow Scorer object.
    
    Args:
        scorer_def: The ScorerDefinition database object.
        
    Returns:
        An MLflow scorer object (metric function or object).
    """
    config = scorer_def.configuration
    
    if scorer_def.scorer_type == ScorerType.BUILTIN:
        # Example: Load 'mlflow.metrics.genai.toxicity'
        # Config should look like: { "metric_name": "toxicity" }
        metric_name = config.get("metric_name")
        # For builtins, mlflow.genai.evaluate might expect the string name or the metric object.
        # Previous attempts with object failed. Trying string name if it's a standard metric.
        # But wait, custom metrics need objects.
        # Let's try returning the object again but ensure it's instantiated if it's a class, 
        # or just the function if it's a function?
        # The error "invalid item with type: function" means we shouldn't pass the function.
        # The error "invalid item with type: CallableEvaluationMetric" means we shouldn't pass the result of calling it?
        # Actually, let's try passing the STRING "flesch_kincaid_grade_level" directly if it matches.
        
        return metric_name
        
    elif scorer_def.scorer_type == ScorerType.LLM_JUDGE:
        # Uses MLflow 3.0 make_genai_metric
        # Config: { "definition": "...", "grading_prompt": "...", "model": "openai:/gpt-4", "examples": [...] }
        
        examples_data = config.get("examples", [])
        examples = [EvaluationExample(**ex) for ex in examples_data]
        
        return make_genai_metric(
            name=scorer_def.name,
            definition=config.get("definition", ""),
            grading_prompt=config.get("grading_prompt", ""),
            model=config.get("judge_model", "openai:/gpt-4"),
            examples=examples,
            greater_is_better=config.get("greater_is_better", True),
            aggregations=config.get("aggregations", ["mean"]),
            max_workers=config.get("max_workers", 10)
        )
        
    elif scorer_def.scorer_type == ScorerType.CODE:
        # Load custom python logic
        # For MVP, we might skip complex dynamic loading or implement a simple registry
        # Security Warning: Ensure strict sandboxing if allowing raw code
        raise NotImplementedError("Code-based scorers are not yet implemented")
        
    else:
        raise ValueError(f"Unknown scorer type: {scorer_def.scorer_type}")
