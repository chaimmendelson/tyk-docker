from __future__ import annotations

import pytest

from tandoor_mcp.config import ConfigError, Settings


def test_from_env_reads_all_values(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TANDOOR_BASE_URL", "http://example.test:6060/")
    monkeypatch.setenv("TANDOOR_API_TOKEN", "tda_abc123")
    monkeypatch.setenv("TANDOOR_TIMEOUT", "15")

    settings = Settings.from_env()

    assert settings.base_url == "http://example.test:6060"  # trailing slash stripped
    assert settings.api_token == "tda_abc123"
    assert settings.timeout == 15.0


def test_from_env_defaults_base_url_and_timeout(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TANDOOR_BASE_URL", raising=False)
    monkeypatch.delenv("TANDOOR_TIMEOUT", raising=False)
    monkeypatch.setenv("TANDOOR_API_TOKEN", "tda_abc123")

    settings = Settings.from_env()

    assert settings.base_url == "http://127.0.0.1:6060"
    assert settings.timeout == 30.0


def test_from_env_missing_token_raises_config_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TANDOOR_API_TOKEN", raising=False)

    with pytest.raises(ConfigError, match="TANDOOR_API_TOKEN"):
        Settings.from_env()


def test_from_env_empty_token_raises_config_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TANDOOR_API_TOKEN", "")

    with pytest.raises(ConfigError, match="TANDOOR_API_TOKEN"):
        Settings.from_env()


def test_from_env_invalid_timeout_raises_config_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TANDOOR_API_TOKEN", "tda_abc123")
    monkeypatch.setenv("TANDOOR_TIMEOUT", "not-a-number")

    with pytest.raises(ConfigError, match="TANDOOR_TIMEOUT"):
        Settings.from_env()


def test_settings_is_frozen():
    settings = Settings(base_url="http://x", api_token="t")
    with pytest.raises(AttributeError):
        settings.api_token = "other"  # type: ignore[misc]
