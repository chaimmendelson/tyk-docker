"""Exceptions raised by the Tandoor API client."""

from __future__ import annotations

from typing import Any


class TandoorAPIError(Exception):
    """Raised when the Tandoor API returns an error response or is unreachable."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        if self.status_code is not None:
            return f"[{self.status_code}] {base}"
        return base
