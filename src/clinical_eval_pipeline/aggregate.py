from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from clinical_eval_pipeline.scoring.deterministic import normalize_text


def compute_aggregates(
    scored_df: pd.DataFrame,
    semantic_repro_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    df = scored_df.copy()
    if "normalized_response" not in df.columns:
        df["normalized_response"] = df["response_text"].astype(str).map(normalize_text)
    if "normalized_gold" not in df.columns:
        df["normalized_gold"] = df["gold_answer"].astype(str).map(normalize_text)

    df["response_len"] = df["response_text"].astype(str).str.len()
    df["is_unique_response"] = (
        df.groupby(["model", "question_id"])["response_text"].transform("nunique")
        / df.groupby(["model", "question_id"])["response_text"].transform("size")
    )
    df["is_unique_normalized_response"] = (
        df.groupby(["model", "question_id"])["normalized_response"].transform("nunique")
        / df.groupby(["model", "question_id"])["normalized_response"].transform("size")
    )

    metrics = [
        "exact_match",
        "normalized_exact_match",
        "token_f1",
        "string_similarity",
        "bleu",
        "rouge_l",
        "bertscore_precision",
        "bertscore_recall",
        "bertscore_f1",
    ]
    metrics = [m for m in metrics if m in df.columns]
    if "judge_score" in df.columns:
        metrics.append("judge_score")

    grouped = df.groupby(["model", "question_id"], dropna=False)
    agg = grouped[metrics].agg(["mean", "median", "std", "min", "max"]).reset_index()
    agg.columns = ["_".join([c for c in col if c]).rstrip("_") for col in agg.columns.to_flat_index()]

    extra = grouped.agg(
        n_runs=("run_index", "count"),
        unique_responses=("response_text", "nunique"),
        unique_normalized_responses=("normalized_response", "nunique"),
        avg_response_length=("response_len", "mean"),
    ).reset_index()
    extra["response_uniqueness_rate"] = extra["unique_responses"] / extra["n_runs"].replace(0, np.nan)
    extra["normalized_response_uniqueness_rate"] = (
        extra["unique_normalized_responses"] / extra["n_runs"].replace(0, np.nan)
    )
    modal_counts = (
        df.groupby(["model", "question_id", "normalized_response"], dropna=False)
        .size()
        .reset_index(name="count")
        .groupby(["model", "question_id"], dropna=False)["count"]
        .max()
        .reset_index(name="modal_normalized_response_count")
    )
    extra = extra.merge(modal_counts, on=["model", "question_id"], how="left")
    extra["normalized_self_agreement_rate"] = (
        extra["modal_normalized_response_count"] / extra["n_runs"].replace(0, np.nan)
    )

    result = agg.merge(extra, on=["model", "question_id"], how="left")
    if semantic_repro_df is not None and not semantic_repro_df.empty:
        result = result.merge(semantic_repro_df, on=["model", "question_id"], how="left")
    return result


def _bootstrap_ci(
    values: np.ndarray,
    *,
    n_boot: int = 1000,
    ci: float = 0.95,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of ``values`` (resampling units)."""
    values = values[~np.isnan(values)]
    if values.size == 0:
        return (float("nan"), float("nan"))
    if values.size == 1:
        return (float(values[0]), float(values[0]))
    idx = rng.integers(0, values.size, size=(n_boot, values.size))
    boot_means = values[idx].mean(axis=1)
    lo = (1.0 - ci) / 2.0 * 100.0
    hi = (1.0 + ci) / 2.0 * 100.0
    return (float(np.percentile(boot_means, lo)), float(np.percentile(boot_means, hi)))


def model_level_summary(
    aggregate_df: pd.DataFrame,
    per_question_cols: list[str],
    *,
    n_boot: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> pd.DataFrame:
    """Model-level mean and bootstrap CI for each per-question column.

    The unit of analysis is the *question*: each metric's model-level point
    estimate is the mean of its per-question values, and the 95% CI is obtained
    by resampling questions with replacement (clustered bootstrap). With a
    balanced design (equal runs per question) the per-question-mean average
    equals the response-pooled mean, so this matches Tables 1 & 2 while adding
    principled uncertainty. Returns one row per model with ``<col>_mean``,
    ``<col>_ci_low``, ``<col>_ci_high`` and ``n_questions``.
    """
    rng = np.random.default_rng(seed)
    cols = [c for c in per_question_cols if c in aggregate_df.columns]
    rows: list[dict[str, object]] = []
    for model, group in aggregate_df.groupby("model", sort=False):
        row: dict[str, object] = {"model": model, "n_questions": int(len(group))}
        for col in cols:
            values = pd.to_numeric(group[col], errors="coerce").to_numpy(dtype="float64")
            clean = values[~np.isnan(values)]
            row[f"{col}_mean"] = float(clean.mean()) if clean.size else float("nan")
            lo, hi = _bootstrap_ci(values, n_boot=n_boot, ci=ci, rng=rng)
            row[f"{col}_ci_low"] = lo
            row[f"{col}_ci_high"] = hi
        rows.append(row)
    return pd.DataFrame(rows)


def save_aggregates(aggregate_df: pd.DataFrame, output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "aggregates.csv"
    aggregate_df.to_csv(path, index=False)
    return path
