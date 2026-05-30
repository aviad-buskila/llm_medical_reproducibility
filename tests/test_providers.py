import pytest

from clinical_eval_pipeline.config import GenerationConfig
from clinical_eval_pipeline.providers import OllamaProvider, Provider, build_provider


def _gen_cfg() -> GenerationConfig:
    return GenerationConfig(temperature=0.2, top_p=1.0, max_tokens=512)


def test_build_provider_ollama_default() -> None:
    provider = build_provider("ollama", base_url="http://localhost:11434", generation_config=_gen_cfg())
    assert isinstance(provider, OllamaProvider)
    # Structural typing: the Ollama provider satisfies the Provider protocol.
    assert isinstance(provider, Provider)


def test_build_provider_is_case_insensitive() -> None:
    provider = build_provider("OLLAMA", base_url="http://localhost:11434", generation_config=_gen_cfg())
    assert isinstance(provider, OllamaProvider)


def test_build_provider_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown provider"):
        build_provider("vertex", base_url="http://localhost:11434", generation_config=_gen_cfg())


def test_build_provider_openai_without_sdk_raises_clear_error() -> None:
    # openai SDK is not installed in this env; the provider must surface a
    # clear, actionable error rather than a bare ModuleNotFoundError.
    with pytest.raises(ImportError, match="pip install openai"):
        build_provider("openai", base_url="http://localhost:11434", generation_config=_gen_cfg())


def test_build_provider_anthropic_without_sdk_raises_clear_error() -> None:
    with pytest.raises(ImportError, match="pip install anthropic"):
        build_provider("anthropic", base_url="http://localhost:11434", generation_config=_gen_cfg())
