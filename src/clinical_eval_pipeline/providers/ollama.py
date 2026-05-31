from __future__ import annotations

from typing import Any

from clinical_eval_pipeline.config import GenerationConfig
from clinical_eval_pipeline.ollama_client import OllamaClient


class OllamaProvider:
    """Provider backed by the local Ollama runtime (the default)."""

    def __init__(self, *, base_url: str, generation_config: GenerationConfig) -> None:
        self._client = OllamaClient(base_url=base_url, generation_config=generation_config)

    def generate(
        self,
        model: str,
        prompt: str,
        seed: int | None = None,
        system: str | None = None,
    ) -> dict[str, Any]:
        return self._client.generate(model=model, prompt=prompt, seed=seed, system=system)
