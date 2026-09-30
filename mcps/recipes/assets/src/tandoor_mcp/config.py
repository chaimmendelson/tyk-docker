"""Runtime configuration, read from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str
    api_token: str
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> Settings:
        base_url = os.environ.get("TANDOOR_BASE_URL", "http://127.0.0.1:6060").rstrip("/")
        token = os.environ.get("TANDOOR_API_TOKEN")
        if not token:
            raise ConfigError(
                "TANDOOR_API_TOKEN is not set. Export it or put it in a .env file "
                "loaded by your process manager before starting the server."
            )
        timeout_raw = os.environ.get("TANDOOR_TIMEOUT", "30")
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ConfigError(f"TANDOOR_TIMEOUT must be a number, got {timeout_raw!r}") from exc

        return cls(base_url=base_url, api_token=token, timeout=timeout)
