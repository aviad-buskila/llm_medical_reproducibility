import random

import numpy as np
import pandas as pd

from clinical_eval_pipeline.aggregate import (
    _bootstrap_ci,
    compute_aggregates,
    model_level_summary,
)
from clinical_eval_pipeline.scoring.semantic import _group_pairs


def _scored_fixture() -> pd.DataFrame:
    rows = []
    for q in ["q1", "q2"]:
        for i in range(4):
            rows.append(
                {
                    "model": "m1",
                    "question_id": q,
                    "run_index": i,
                    "response_text": f"answer {q} variant {i % 2}",
                    "gold_answer": "gold",
                    "exact_match": 0.0,
                    "normalized_exact_match": 0.0,
                    "token_f1": 0.5 + 0.01 * i,
                    "bertscore_f1": 0.8,
                }
            )
    return pd.DataFrame(rows)


def test_group_pairs_all_when_small() -> None:
    rng = random.Random(0)
    assert _group_pairs(4, max_pairs=45, rng=rng) == [
        (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3),
    ]


def test_group_pairs_capped_is_deterministic() -> None:
    pairs_a = _group_pairs(20, max_pairs=10, rng=random.Random(42))
    pairs_b = _group_pairs(20, max_pairs=10, rng=random.Random(42))
    assert len(pairs_a) == 10
    assert pairs_a == pairs_b
    assert all(i < j for i, j in pairs_a)


def test_group_pairs_single_run_empty() -> None:
    assert _group_pairs(1, max_pairs=45, rng=random.Random(0)) == []


def test_bootstrap_ci_brackets_mean() -> None:
    rng = np.random.default_rng(0)
    values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    lo, hi = _bootstrap_ci(values, n_boot=2000, ci=0.95, rng=rng)
    assert lo <= values.mean() <= hi
    assert lo < hi


def test_bootstrap_ci_handles_nan_and_singletons() -> None:
    rng = np.random.default_rng(0)
    lo, hi = _bootstrap_ci(np.array([np.nan, 0.7]), n_boot=100, ci=0.95, rng=rng)
    assert lo == hi == 0.7
    lo, hi = _bootstrap_ci(np.array([np.nan, np.nan]), n_boot=100, ci=0.95, rng=rng)
    assert np.isnan(lo) and np.isnan(hi)


def test_compute_aggregates_merges_semantic() -> None:
    scored = _scored_fixture()
    semantic = pd.DataFrame(
        [
            {"model": "m1", "question_id": "q1", "semantic_self_similarity_mean": 0.91,
             "semantic_self_similarity_std": 0.02, "n_semantic_pairs": 6},
            {"model": "m1", "question_id": "q2", "semantic_self_similarity_mean": 0.88,
             "semantic_self_similarity_std": 0.03, "n_semantic_pairs": 6},
        ]
    )
    agg = compute_aggregates(scored, semantic)
    assert "semantic_self_similarity_mean" in agg.columns
    assert set(agg["semantic_self_similarity_mean"]) == {0.91, 0.88}


def test_compute_aggregates_without_semantic_unchanged() -> None:
    agg = compute_aggregates(_scored_fixture())
    assert "semantic_self_similarity_mean" not in agg.columns
    assert "normalized_self_agreement_rate" in agg.columns


def test_model_level_summary_columns_and_ci() -> None:
    scored = _scored_fixture()
    agg = compute_aggregates(scored)
    summary = model_level_summary(
        agg, ["token_f1_mean", "normalized_self_agreement_rate"], n_boot=500, seed=1
    )
    assert list(summary["model"]) == ["m1"]
    for col in ["token_f1_mean", "normalized_self_agreement_rate"]:
        assert f"{col}_mean" in summary.columns
        assert f"{col}_ci_low" in summary.columns
        assert f"{col}_ci_high" in summary.columns
        row = summary.iloc[0]
        assert row[f"{col}_ci_low"] <= row[f"{col}_mean"] <= row[f"{col}_ci_high"]
