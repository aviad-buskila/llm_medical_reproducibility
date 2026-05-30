"""Semantic reproducibility metric.

The lexical reproducibility metrics (``normalized_self_agreement_rate`` and
``normalized_response_uniqueness_rate`` in :mod:`clinical_eval_pipeline.aggregate`)
count two medically equivalent but paraphrased answers as *different* outputs.
This module adds a complementary semantic measure: for each (model, question)
pair we embed the ``N`` repeated run outputs and compute the mean pairwise
semantic similarity across them, reusing the same BERTScore backbone already
used for the model-vs-gold quality metrics in
:mod:`clinical_eval_pipeline.scoring.deterministic`.

A value near 1.0 means the model expresses the *same content* on every run even
when the surface wording differs; a low value means the runs diverge in meaning,
not merely in phrasing.
"""

from __future__ import annotations

import itertools
import random

import pandas as pd

from clinical_eval_pipeline.scoring.deterministic import _bert_scores


def _group_pairs(n: int, max_pairs: int, rng: random.Random) -> list[tuple[int, int]]:
    """Return index pairs (i<j) for a group of ``n`` runs.

    Uses all C(n, 2) pairs when that is <= ``max_pairs``; otherwise draws a
    deterministic sample so the metric stays tractable for large ``N`` while
    remaining exact in the production regime (N=10 -> 45 pairs).
    """
    all_pairs = list(itertools.combinations(range(n), 2))
    if max_pairs is not None and len(all_pairs) > max_pairs:
        return rng.sample(all_pairs, max_pairs)
    return all_pairs


def compute_semantic_reproducibility(
    scored_df: pd.DataFrame,
    *,
    model_type: str = "roberta-base",
    batch_size: int = 8,
    max_pairs_per_group: int = 45,
    seed: int = 42,
) -> pd.DataFrame:
    """Per-(model, question) semantic self-similarity across repeated runs.

    Returns a DataFrame with columns ``model``, ``question_id``,
    ``semantic_self_similarity_mean``, ``semantic_self_similarity_std`` and
    ``n_semantic_pairs``. Groups with fewer than two runs yield NaN similarity
    (a pairwise notion is undefined for a single output).
    """
    rng = random.Random(seed)

    cand: list[str] = []
    ref: list[str] = []
    pair_group_keys: list[tuple[str, str]] = []
    group_n_runs: dict[tuple[str, str], int] = {}

    for (model, question_id), group in scored_df.groupby(["model", "question_id"], sort=False):
        responses = group["response_text"].astype(str).tolist()
        group_n_runs[(model, question_id)] = len(responses)
        for i, j in _group_pairs(len(responses), max_pairs_per_group, rng):
            cand.append(responses[i])
            ref.append(responses[j])
            pair_group_keys.append((model, question_id))

    if cand:
        _, _, f1 = _bert_scores(cand, ref, model_type=model_type, batch_size=batch_size)
    else:
        f1 = []

    sims_by_group: dict[tuple[str, str], list[float]] = {}
    for key, score in zip(pair_group_keys, f1, strict=True):
        sims_by_group.setdefault(key, []).append(score)

    records: list[dict[str, object]] = []
    for key, n_runs in group_n_runs.items():
        model, question_id = key
        sims = sims_by_group.get(key, [])
        sims_series = pd.Series(sims, dtype="float64")
        records.append(
            {
                "model": model,
                "question_id": question_id,
                "semantic_self_similarity_mean": sims_series.mean() if len(sims) else pd.NA,
                "semantic_self_similarity_std": sims_series.std(ddof=0) if len(sims) > 1 else pd.NA,
                "n_semantic_pairs": len(sims),
            }
        )

    return pd.DataFrame.from_records(
        records,
        columns=[
            "model",
            "question_id",
            "semantic_self_similarity_mean",
            "semantic_self_similarity_std",
            "n_semantic_pairs",
        ],
    )
