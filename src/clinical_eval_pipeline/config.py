from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError


class ModelConfig(BaseModel):
    name: str
    runs_per_prompt: int | None = Field(default=None, ge=1)
    provider: str = "ollama"


class GenerationConfig(BaseModel):
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = Field(default=256, ge=1)
    timeout_seconds: int = Field(default=120, ge=1)
    retries: int = Field(default=2, ge=0)


class JudgeConfig(BaseModel):
    enabled: bool = False
    model: str | None = None
    use_chat_api: bool = True
    rubric_prompt: str = (
        "You are a strict clinical evaluator.\n"
        "Given QUESTION, GOLD_ANSWER and MODEL_ANSWER, score factual correctness from 0 to 1.\n"
        "Respond only as: score=<float> rationale=<brief reason>"
    )
    # Judge-reliability sub-study (Reviewer #2): re-judge a stratified subset of
    # responses multiple times to quantify the judge's own stochasticity.
    reliability_passes: int = Field(default=5, ge=2)
    reliability_subset: int = Field(default=25, ge=1)


class OutputConfig(BaseModel):
    output_dir: str = "outputs"
    log_subdir: str = "logs"
    save_parquet: bool = True
    save_csv: bool = True
    save_jsonl: bool = True


class PipelineConfig(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    prompt_file: str = "data/gold_data.csv"
    shared_instruction: str | None = None
    models: list[ModelConfig]
    runs_per_prompt: int = Field(default=100, ge=1)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    deterministic_mode: bool = True
    verbose: bool = True
    resume: bool = False
    bertscore_model: str = "roberta-base"
    bertscore_batch_size: int = Field(default=8, ge=1)
    random_seed: int | None = None
    report_format: Literal["markdown"] = "markdown"
    semantic_reproducibility: bool = True
    semantic_max_pairs_per_group: int = Field(default=45, ge=1)
    bootstrap_resamples: int = Field(default=1000, ge=1)
    bootstrap_ci: float = Field(default=0.95, gt=0.0, lt=1.0)


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        return PipelineConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid pipeline config at {config_path}:\n{exc}") from exc
