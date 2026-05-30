"""Inference provider abstraction.

The pipeline was originally Ollama-only. To let the evaluation include a
closed-source API model (Reviewer #1) alongside the local open-weight models,
generation is routed through a small ``Provider`` protocol whose single method
matches the contract the runner already depends on::

    generate(model, prompt, seed=None, system=None) -> dict

The returned dict must carry at least ``response`` and, where available,
``total_duration`` (ns), ``eval_count`` and ``prompt_eval_count`` so the
existing efficiency scoring keeps working unchanged.
"""

from __future__ import annotations

from clinical_eval_pipeline.config import GenerationConfig
from clinical_eval_pipeline.providers.base import Provider
from clinical_eval_pipeline.providers.ollama import OllamaProvider

__all__ = ["Provider", "OllamaProvider", "build_provider"]


def build_provider(
    provider: str,
    *,
    base_url: str,
    generation_config: GenerationConfig,
) -> Provider:
    """Return a provider instance for the given provider name.

    Closed-source SDKs (``openai``, ``anthropic``) are imported lazily inside
    their providers, so this factory and the Ollama path work without those
    packages installed.
    """
    key = provider.strip().lower()
    if key == "ollama":
        return OllamaProvider(base_url=base_url, generation_config=generation_config)
    if key == "openai":
        from clinical_eval_pipeline.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(generation_config=generation_config)
    if key == "anthropic":
        from clinical_eval_pipeline.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(generation_config=generation_config)
    raise ValueError(
        f"Unknown provider '{provider}'. Supported: 'ollama', 'openai', 'anthropic'."
    )
