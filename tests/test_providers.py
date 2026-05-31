import pytest

from clinical_eval_pipeline.config import GenerationConfig
from clinical_eval_pipeline.providers import OllamaProvider, Provider, build_provider
from clinical_eval_pipeline.providers.retry import ProviderRequestError, call_with_retries


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


def test_build_provider_openai_requires_sdk_and_key(monkeypatch) -> None:
    # Without a usable setup the provider must surface a clear, actionable error:
    # ImportError if the SDK is absent, RuntimeError if the API key is unset.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises((ImportError, RuntimeError)):
        build_provider("openai", base_url="http://localhost:11434", generation_config=_gen_cfg())


def test_build_provider_anthropic_requires_sdk_and_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises((ImportError, RuntimeError)):
        build_provider("anthropic", base_url="http://localhost:11434", generation_config=_gen_cfg())


def test_call_with_retries_returns_on_success() -> None:
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        return "ok"

    assert call_with_retries(fn, retries=2, base_delay=0.0) == "ok"
    assert calls["n"] == 1


def test_call_with_retries_recovers_after_transient_failures() -> None:
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("transient 429")
        return "recovered"

    assert call_with_retries(fn, retries=2, base_delay=0.0) == "recovered"
    assert calls["n"] == 3


def test_call_with_retries_raises_after_exhaustion() -> None:
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise RuntimeError("still failing")

    with pytest.raises(ProviderRequestError, match="failed after 3 attempts"):
        call_with_retries(fn, retries=2, base_delay=0.0, label="test")
    assert calls["n"] == 3
