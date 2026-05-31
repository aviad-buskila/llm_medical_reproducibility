import pandas as pd

from clinical_eval_pipeline import runner as runner_mod
from clinical_eval_pipeline.config import ModelConfig, OutputConfig, PipelineConfig


class _FakeProvider:
    def __init__(self, counter: dict) -> None:
        self._counter = counter

    def generate(self, model, prompt, seed=None, system=None):
        self._counter["n"] += 1
        return {
            "response": f"answer to {prompt} #{self._counter['n']}",
            "done": True,
            "total_duration": 1_000_000,
            "eval_count": 5,
            "prompt_eval_count": 3,
        }


def _questions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"id": "q1", "question": "What is A?", "gold_answer": "A.", "category": ""},
            {"id": "q2", "question": "What is B?", "gold_answer": "B.", "category": ""},
        ]
    )


def _config(tmp_path, runs: int) -> PipelineConfig:
    return PipelineConfig(
        models=[ModelConfig(name="m1")],
        runs_per_prompt=runs,
        deterministic_mode=False,
        output=OutputConfig(output_dir=str(tmp_path)),
    )


def _install_fake_provider(monkeypatch, counter):
    monkeypatch.setattr(runner_mod, "build_provider", lambda *a, **k: _FakeProvider(counter))


def test_fresh_run_writes_incremental_jsonl(tmp_path, monkeypatch) -> None:
    counter = {"n": 0}
    _install_fake_provider(monkeypatch, counter)
    df = runner_mod.run_evaluations(_config(tmp_path, runs=2), _questions(), resume=False)
    assert len(df) == 4  # 1 model x 2 questions x 2 runs
    assert counter["n"] == 4
    jsonl = (tmp_path / "raw_responses.jsonl").read_text().strip().splitlines()
    assert len(jsonl) == 4


def test_resume_skips_completed_and_does_not_call_provider(tmp_path, monkeypatch) -> None:
    counter = {"n": 0}
    _install_fake_provider(monkeypatch, counter)
    cfg = _config(tmp_path, runs=2)
    runner_mod.run_evaluations(cfg, _questions(), resume=False)
    assert counter["n"] == 4

    # Re-run with resume: everything is already in the checkpoint, so the
    # provider must not be invoked at all.
    df = runner_mod.run_evaluations(cfg, _questions(), resume=True)
    assert counter["n"] == 4  # unchanged
    assert len(df) == 4


def test_resume_generates_only_missing_runs(tmp_path, monkeypatch) -> None:
    counter = {"n": 0}
    _install_fake_provider(monkeypatch, counter)
    # First pass: 1 run per question -> 2 responses.
    runner_mod.run_evaluations(_config(tmp_path, runs=1), _questions(), resume=False)
    assert counter["n"] == 2

    # Resume with 2 runs per question -> only run_index=1 for each question is new.
    df = runner_mod.run_evaluations(_config(tmp_path, runs=2), _questions(), resume=True)
    assert counter["n"] == 4  # 2 new calls only
    assert len(df) == 4
    # JSONL holds the complete, de-duplicated set.
    jsonl = (tmp_path / "raw_responses.jsonl").read_text().strip().splitlines()
    assert len(jsonl) == 4
