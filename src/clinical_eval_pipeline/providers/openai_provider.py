from __future__ import annotations

import os
import time
from typing import Any

from clinical_eval_pipeline.config import GenerationConfig


class OpenAIProvider:
    """Provider backed by the OpenAI chat-completions API.

    Used to include one closed-source reference model (e.g. ``gpt-4o-mini``)
    alongside the local open-weight models. Latency is measured client-side and
    written to ``total_duration`` (ns) so throughput scoring stays comparable;
    token counts come from the API ``usage`` block. OpenAI honours ``seed`` on a
    best-effort basis (documented as a determinism caveat in the manuscript).
    """

    def __init__(self, *, generation_config: GenerationConfig) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - exercised only without the SDK
            raise ImportError(
                "The 'openai' package is required for provider='openai'. "
                "Install it with `pip install openai` and set OPENAI_API_KEY."
            ) from exc

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set; required for provider='openai'."
            )
        self._client = OpenAI(api_key=api_key)
        self._cfg = generation_config

    def generate(
        self,
        model: str,
        prompt: str,
        seed: int | None = None,
        system: str | None = None,
    ) -> dict[str, Any]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": self._cfg.temperature,
            "top_p": self._cfg.top_p,
            "max_tokens": self._cfg.max_tokens,
        }
        if seed is not None:
            kwargs["seed"] = seed

        start = time.perf_counter()
        completion = self._client.chat.completions.create(**kwargs)
        elapsed_ns = int((time.perf_counter() - start) * 1_000_000_000)

        text = completion.choices[0].message.content or ""
        usage = getattr(completion, "usage", None)
        return {
            "model": model,
            "prompt": prompt,
            "response": text,
            "done": True,
            "total_duration": elapsed_ns,
            "eval_count": getattr(usage, "completion_tokens", None),
            "prompt_eval_count": getattr(usage, "prompt_tokens", None),
        }
