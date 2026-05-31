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


def _completed_keys_from_jsonl(jsonl_path: Path) -> tuple[list[dict[str, Any]], set[tuple[str, str, int]]]:
    """Read an existing JSONL checkpoint, returning its rows and completed keys.

    A response is keyed by (model, question_id, run_index); these keys let a
    resumed run skip work already on disk.
    """
    rows: list[dict[str, Any]] = []
    completed: set[tuple[str, str, int]] = set()
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rows.append(rec)
            completed.add((str(rec["model"]), str(rec["question_id"]), int(rec["run_index"])))
    return rows, completed


def run_evaluations(
    config: PipelineConfig,
    questions: pd.DataFrame,
    resume: bool = False,
) -> pd.DataFrame:
    """Query each model for each question N times, persisting incrementally.

    Each response is appended to ``raw_responses.jsonl`` as soon as it returns,
    so an interrupted run loses no completed work. When ``resume`` is set and a
    JSONL checkpoint exists, already-completed (model, question, run) triples are
    skipped and generation continues where it left off. Parquet/CSV snapshots are
    (re)written from the full set at the end.
    """
    out_dir = Path(config.output.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "raw_responses.jsonl"

    rows: list[dict[str, Any]] = []
    completed: set[tuple[str, str, int]] = set()
    resuming = resume and jsonl_path.exists()
    if resuming:
        rows, completed = _completed_keys_from_jsonl(jsonl_path)
        print(f"[run] resume: found {len(completed)} completed responses in checkpoint; continuing", flush=True)

    total_calls = sum((m.runs_per_prompt or config.runs_per_prompt) * len(questions) for m in config.models)
    completed_calls = len(completed)
    shared_system_instruction = (config.shared_instruction or "").strip() or None

    # Append when resuming an existing checkpoint, else start a fresh JSONL.
    sink_mode = "a" if resuming else "w"
    sink = jsonl_path.open(sink_mode, encoding="utf-8") if config.output.save_jsonl else None
    try:
        for model_cfg in config.models:
            runs = model_cfg.runs_per_prompt or config.runs_per_prompt
            # Build the provider lazily, only when there is actual work for this
            # model. This avoids requiring API keys (e.g. for the closed model)
            # when a fully-completed run is merely being resumed.
            provider = None
            if config.verbose:
                print(
                    f"[run] model={model_cfg.name} provider={model_cfg.provider} "
                    f"runs_per_prompt={runs} prompts={len(questions)}",
                    flush=True,
                )
            for _, question_row in questions.iterrows():
                qid = str(question_row["id"])
                for run_index in range(runs):
                    if (str(model_cfg.name), qid, run_index) in completed:
                        continue
                    if provider is None:
                        provider = build_provider(
                            model_cfg.provider,
                            base_url=config.ollama_base_url,
                            generation_config=config.generation,
                        )

                    seed = None
                    if config.deterministic_mode and config.random_seed is not None:
                        seed = config.random_seed + run_index

                    if config.verbose:
                        print(
                            f"[run] request {completed_calls + 1}/{total_calls} "
                            f"model={model_cfg.name} question_id={qid} run={run_index}",
                            flush=True,
                        )
                    response = provider.generate(
                        model=model_cfg.name,
                        prompt=str(question_row["question"]),
                        seed=seed,
                        system=shared_system_instruction,
                    )
                    record = {
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
                    if sink is not None:
                        sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                        sink.flush()
                    rows.append(record)
                    completed.add((str(model_cfg.name), qid, run_index))
                    completed_calls += 1
                    if config.verbose:
                        print(
                            f"[run] completed {completed_calls}/{total_calls} "
                            f"model={model_cfg.name} question_id={qid} run={run_index}",
                            flush=True,
                        )
    finally:
        if sink is not None:
            sink.close()

    df = pd.DataFrame(rows)
    # JSONL was already written incrementally; (re)write parquet/csv snapshots.
    if config.output.save_parquet:
        df.to_parquet(out_dir / "raw_responses.parquet", index=False)
    if config.output.save_csv:
        df.to_csv(out_dir / "raw_responses.csv", index=False)
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
