from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from clinical_eval_pipeline.config import PipelineConfig
from clinical_eval_pipeline.providers import build_provider


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def run_evaluations(config: PipelineConfig, questions: pd.DataFrame) -> pd.DataFrame:
    out_dir = Path(config.output.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    total_calls = sum((m.runs_per_prompt or config.runs_per_prompt) * len(questions) for m in config.models)
    completed_calls = 0
    shared_system_instruction = (config.shared_instruction or "").strip() or None

    for model_cfg in config.models:
        runs = model_cfg.runs_per_prompt or config.runs_per_prompt
        provider = build_provider(
            model_cfg.provider,
            base_url=config.ollama_base_url,
            generation_config=config.generation,
        )
        if config.verbose:
            print(
                f"[run] model={model_cfg.name} provider={model_cfg.provider} "
                f"runs_per_prompt={runs} prompts={len(questions)}",
                flush=True,
            )
        for _, question_row in questions.iterrows():
            for run_index in range(runs):
                seed = None
                if config.deterministic_mode and config.random_seed is not None:
                    seed = config.random_seed + run_index

                if config.verbose:
                    print(
                        f"[run] request {completed_calls + 1}/{total_calls} "
                        f"model={model_cfg.name} question_id={question_row['id']} run={run_index}",
                        flush=True,
                    )
                response = provider.generate(
                    model=model_cfg.name,
                    prompt=str(question_row["question"]),
                    seed=seed,
                    system=shared_system_instruction,
                )
                rows.append(
                    {
                        "timestamp_utc": _now_iso(),
                        "model": model_cfg.name,
                        "provider": model_cfg.provider,
                        "question_id": question_row["id"],
                        "question": question_row["question"],
                        "gold_answer": question_row["gold_answer"],
                        "category": question_row.get("category", ""),
                        "run_index": run_index,
                        "seed": seed,
                        "response_text": str(response.get("response", "")),
                        "done": bool(response.get("done", False)),
                        "total_duration": response.get("total_duration"),
                        "eval_count": response.get("eval_count"),
                        "prompt_eval_count": response.get("prompt_eval_count"),
                        "shared_instruction": shared_system_instruction or "",
                    }
                )
                completed_calls += 1
                if config.verbose:
                    print(
                        f"[run] completed {completed_calls}/{total_calls} "
                        f"model={model_cfg.name} question_id={question_row['id']} run={run_index}",
                        flush=True,
                    )

    df = pd.DataFrame(rows)
    persist_raw_outputs(df, out_dir, config.output.save_jsonl, config.output.save_parquet, config.output.save_csv)
    return df


def persist_raw_outputs(
    df: pd.DataFrame,
    out_dir: Path,
    save_jsonl: bool,
    save_parquet: bool,
    save_csv: bool,
) -> None:
    if save_jsonl:
        jsonl_path = out_dir / "raw_responses.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f:
            for record in df.to_dict(orient="records"):
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    if save_parquet:
        df.to_parquet(out_dir / "raw_responses.parquet", index=False)
    if save_csv:
        df.to_csv(out_dir / "raw_responses.csv", index=False)
