from __future__ import annotations

import os
import time
from typing import Any

from clinical_eval_pipeline.config import GenerationConfig
from clinical_eval_pipeline.providers.retry import call_with_retries


class AnthropicProvider:
    """Provider backed by the Anthropic Messages API.

    Alternative closed-source reference model (e.g. ``claude-haiku-4-5``).
    Anthropic does not expose a sampling ``seed``, so ``seed`` is accepted but
    ignored here; the manuscript notes that the closed model's runs are not
    seed-controlled (a determinism caveat). Latency is measured client-side and
    written to ``total_duration`` (ns); token counts come from ``usage``.
    """

    def __init__(self, *, generation_config: GenerationConfig) -> None:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - exercised only without the SDK
            raise ImportError(
                "The 'anthropic' package is required for provider='anthropic'. "
                "Install it with `pip install anthropic` and set ANTHROPIC_API_KEY."
            ) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set; required for provider='anthropic'."
            )
        # Disable the SDK's own retries so our call_with_retries loop is the
        # single source of retry/backoff; apply the configured request timeout.
        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=float(generation_config.timeout_seconds),
            max_retries=0,
        )
        self._cfg = generation_config

    def generate(
        self,
        model: str,
        prompt: str,
        seed: int | None = None,
        system: str | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature,
            "top_p": self._cfg.top_p,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        start = time.perf_counter()
        message = call_with_retries(
            lambda: self._client.messages.create(**kwargs),
            retries=self._cfg.retries,
            label=f"anthropic model={model}",
        )
        elapsed_ns = int((time.perf_counter() - start) * 1_000_000_000)

        text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
        usage = getattr(message, "usage", None)
        return {
            "model": model,
            "prompt": prompt,
            "response": text,
            "done": True,
            "total_duration": elapsed_ns,
            "eval_count": getattr(usage, "output_tokens", None),
            "prompt_eval_count": getattr(usage, "input_tokens", None),
        }
