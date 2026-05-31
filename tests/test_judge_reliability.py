import math

import pandas as pd

from clinical_eval_pipeline.config import JudgeConfig, ModelConfig, PipelineConfig
from clinical_eval_pipeline.scoring import judge_reliability as jr


def test_icc1_high_when_between_variance_dominates() -> None:
    # Three well-separated targets, tight within-target agreement -> ICC near 1.
    scores = [[0.10, 0.11, 0.09], [0.50, 0.49, 0.51], [0.90, 0.91, 0.89]]
    val = jr.icc1(scores)
    assert 0.9 <= val <= 1.0


def test_icc1_low_when_within_equals_between() -> None:
    # Identical spread within every target -> no reliable between-target signal.
    scores = [[0.2, 0.8], [0.2, 0.8], [0.2, 0.8]]
    val = jr.icc1(scores)
    assert val < 0.1


def test_icc1_undefined_with_one_target() -> None:
    assert math.isnan(jr.icc1([[0.3, 0.4, 0.5]]))


def test_select_subset_is_stratified_by_model() -> None:
    rows = []
    for model in ["a", "b", "c"]:
        for i in range(10):
            rows.append({"model": model, "question_id": f"q{i}", "run_index": i,
                         "question": "Q", "gold_answer": "G", "response_text": f"{model}-{i}"})
    df = pd.DataFrame(rows)
    subset = jr.select_reliability_subset(df, subset_n=6, seed=1)
    assert len(subset) == 6
    # Each model represented (6 // 3 = 2 per model).
    assert set(subset["model"]) == {"a", "b", "c"}


def _config() -> PipelineConfig:
    return PipelineConfig(
        models=[ModelConfig(name="m1")],
        judge=JudgeConfig(enabled=True, model="judge:test", reliability_passes=4, reliability_subset=4),
        random_seed=42,
    )


def test_run_judge_reliability_offline(monkeypatch) -> None:
    rows = []
    for model in ["m1", "m2"]:
        for i in range(4):
            rows.append({"model": model, "question_id": f"q{i}", "run_index": i,
                         "question": "What is X?", "gold_answer": "X is Y.",
                         "response_text": f"{model} answer {i}"})
    scored = pd.DataFrame(rows)

    # Deterministic fake judge: stable base score per response, tiny per-pass jitter.
    calls = {"n": 0}

    def fake_score_response(client, judge_cfg, question, gold_answer, model_answer):
        calls["n"] += 1
        base = (hash(model_answer) % 50) / 100.0  # 0.00..0.49, stable per response
        jitter = 0.01 * (calls["n"] % 3)
        return base + jitter, f"score={base + jitter}"

    monkeypatch.setattr(jr, "score_response", fake_score_response)

    long_scores, summary = jr.run_judge_reliability(scored, _config())
    assert set(["passes", "n_responses", "mean_within_response_std", "icc1"]).issubset(summary)
    assert summary["passes"] == 4.0
    # subset=4 responses, 4 passes each -> 16 judge calls / rows.
    assert len(long_scores) == 16
    assert summary["n_responses"] == 4.0
