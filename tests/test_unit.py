"""Unit tests for the application's environment-driven helper functions."""

from app import fault_injection_enabled, get_environment


def test_get_environment_defaults_to_development(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)

    assert get_environment() == "development"


def test_get_environment_returns_configured_value(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")

    assert get_environment() == "staging"


def test_fault_injection_is_disabled_when_unset(monkeypatch):
    monkeypatch.delenv("ENABLE_FAULT_INJECTION", raising=False)

    assert fault_injection_enabled() is False


def test_fault_injection_accepts_case_insensitive_true(monkeypatch):
    monkeypatch.setenv("ENABLE_FAULT_INJECTION", "  TRUE ")

    assert fault_injection_enabled() is True


def test_fault_injection_rejects_non_true_values(monkeypatch):
    for value in ("false", "1", "yes", "enabled", ""):
        monkeypatch.setenv("ENABLE_FAULT_INJECTION", value)

        assert fault_injection_enabled() is False
