from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """Minimal generation interface shared by local and API backends."""

    def generate(
        self,
        model: str,
        prompt: str,
        seed: int | None = None,
        system: str | None = None,
    ) -> dict[str, Any]:
        """Generate one completion and return a response dict.

        The dict should contain ``response`` (str) and, when the backend can
        report them, ``total_duration`` (ns), ``eval_count`` (output tokens) and
        ``prompt_eval_count`` (prompt tokens) so efficiency scoring works.
        """
        ...
