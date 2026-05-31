"""Load environment variables from a project-root ``.env`` file."""

from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    # src/clinical_eval_pipeline/env.py -> repo root
    return Path(__file__).resolve().parents[2]


def load_env() -> None:
    """Populate ``os.environ`` from ``.env`` if present (does not override existing vars)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    for base in (Path.cwd(), _repo_root()):
        env_file = base / ".env"
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            return

    load_dotenv(override=False)
