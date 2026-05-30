from __future__ import annotations

import os

from clinical_eval_pipeline.env import load_env


def test_load_env_reads_dotenv(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=test-key-from-dotenv\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    load_env()

    assert os.environ.get("OPENAI_API_KEY") == "test-key-from-dotenv"


def test_load_env_does_not_override_existing(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "from-shell")

    load_env()

    assert os.environ.get("OPENAI_API_KEY") == "from-shell"
