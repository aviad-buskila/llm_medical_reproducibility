from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


class ProviderRequestError(RuntimeError):
    """Raised when a provider call fails after exhausting retries."""


def call_with_retries(
    fn: Callable[[], T],
    *,
    retries: int,
    base_delay: float = 1.5,
    label: str = "",
) -> T:
    """Call ``fn`` with up to ``retries`` additional attempts on any exception.

    Mirrors the retry/backoff semantics of the Ollama client so the closed-API
    providers survive transient errors (rate limits, timeouts, connection
    resets) during long multi-hundred-call runs instead of crashing the whole
    pipeline. Sleeps ``base_delay * attempt`` between tries (linear backoff).
    """
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as exc:  # broad on purpose for retry safety
            last_error = exc
            print(
                f"[provider][warn] attempt={attempt + 1}/{retries + 1} {label} failed: {exc}",
                flush=True,
            )
            if attempt < retries:
                time.sleep(base_delay * (attempt + 1))
    raise ProviderRequestError(
        f"Provider call failed after {retries + 1} attempts {label}: {last_error}"
    ) from last_error
