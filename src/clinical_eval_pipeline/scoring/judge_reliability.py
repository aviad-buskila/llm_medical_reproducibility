"""Judge-reliability sub-study (Reviewer #2, major comment #2).

The main evaluation judges each response exactly once, so the judge score
carries unquantified variance. This module re-judges a small, model-stratified
subset of responses ``K`` times and quantifies the judge's own stochasticity:
the within-response score standard deviation and a one-way intraclass
correlation coefficient (ICC(1)), the standard test-retest reliability statistic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from clinical_eval_pipeline.config import JudgeConfig, PipelineConfig
from clinical_eval_pipeline.ollama_client import OllamaClient
from clinical_eval_pipeline.scoring.llm_judge import score_response


def select_reliability_subset(
    scored_df: pd.DataFrame, subset_n: int, seed: int = 42
) -> pd.DataFrame:
    """Sample up to ``subset_n`` responses, stratified across models."""
    models = scored_df["model"].dropna().unique().tolist()
    if not models:
        return scored_df.head(0).copy()
    per_model = max(1, subset_n // len(models))
    parts = [
        group.sample(n=min(per_model, len(group)), random_state=seed)
        for _, group in scored_df.groupby("model", sort=False)
    ]
    sampled = pd.concat(parts).head(subset_n).reset_index(drop=True)
    return sampled


def icc1(scores_by_target: list[list[float]]) -> float:
    """One-way random-effects ICC(1) from per-target repeated scores.

    Targets are responses; raters are the K judge passes. Returns NaN when it is
    undefined (fewer than two targets, or zero total variance).
    """
    groups = [np.asarray(s, dtype="float64") for s in scores_by_target if len(s) >= 2]
    n = len(groups)
    if n < 2:
        return float("nan")
    k = float(np.mean([len(g) for g in groups]))
    grand_mean = np.mean(np.concatenate(groups))
    group_means = np.array([g.mean() for g in groups])
    ss_between = sum(len(g) * (gm - grand_mean) ** 2 for g, gm in zip(groups, group_means))
    ss_within = sum(((g - gm) ** 2).sum() for g, gm in zip(groups, group_means))
    df_between = n - 1
    df_within = sum(len(g) for g in groups) - n
    if df_within <= 0:
        return float("nan")
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    denom = ms_between + (k - 1) * ms_within
    if denom == 0:
        return float("nan")
    return float((ms_between - ms_within) / denom)


def run_judge_reliability(
    scored_df: pd.DataFrame, config: PipelineConfig
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Re-judge a stratified subset ``K`` times; return (long_scores, summary).

    ``long_scores`` has one row per (response, pass) with ``judge_score``.
    ``summary`` reports passes, n_responses, mean/median within-response std and
    ICC(1). Requires the judge model to be reachable via Ollama.
    """
    judge_cfg: JudgeConfig = config.judge
    if not judge_cfg.model:
        raise ValueError("Judge reliability requires a configured judge model.")

    subset = select_reliability_subset(
        scored_df, judge_cfg.reliability_subset, seed=config.random_seed or 42
    )
    client = OllamaClient(config.ollama_base_url, config.generation)

    records: list[dict[str, object]] = []
    scores_by_target: list[list[float]] = []
    for resp_idx, (_, row) in enumerate(subset.iterrows()):
        target_scores: list[float] = []
        for pass_idx in range(judge_cfg.reliability_passes):
            parsed, text = score_response(
                client,
                judge_cfg,
                question=str(row["question"]),
                gold_answer=str(row["gold_answer"]),
                model_answer=str(row["response_text"]),
            )
            records.append(
                {
                    "response_idx": resp_idx,
                    "model": row["model"],
                    "question_id": row["question_id"],
                    "run_index": row.get("run_index"),
                    "pass_index": pass_idx,
                    "judge_score": parsed,
                    "judge_text": text,
                }
            )
            if parsed is not None:
                target_scores.append(parsed)
        if len(target_scores) >= 2:
            scores_by_target.append(target_scores)

    long_scores = pd.DataFrame(records)
    per_target_std = [float(np.std(s, ddof=1)) for s in scores_by_target]
    summary = {
        "passes": float(judge_cfg.reliability_passes),
        "n_responses": float(len(scores_by_target)),
        "mean_within_response_std": float(np.mean(per_target_std)) if per_target_std else float("nan"),
        "median_within_response_std": float(np.median(per_target_std)) if per_target_std else float("nan"),
        "icc1": icc1(scores_by_target),
    }
    return long_scores, summary
