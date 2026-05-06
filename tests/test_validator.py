"""Tests for envdiff.validator."""

import pytest

from envdiff.validator import validate, ValidationResult


@pytest.fixture()
def base_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "DEBUG": "false",
    }


def test_valid_env_returns_is_valid(base_env):
    result = validate(base_env, required=["DATABASE_URL", "SECRET_KEY"])
    assert result.is_valid


def test_missing_required_key_flagged():
    env = {"SECRET_KEY": "abc"}
    result = validate(env, required=["DATABASE_URL", "SECRET_KEY"])
    assert "DATABASE_URL" in result.missing_required
    assert not result.is_valid


def test_empty_required_value_flagged():
    env = {"DATABASE_URL": "", "SECRET_KEY": "abc"}
    result = validate(env, required=["DATABASE_URL", "SECRET_KEY"], allow_empty=False)
    assert "DATABASE_URL" in result.empty_values
    assert not result.is_valid


def test_allow_empty_suppresses_empty_flag():
    env = {"DATABASE_URL": "", "SECRET_KEY": "abc"}
    result = validate(env, required=["DATABASE_URL", "SECRET_KEY"], allow_empty=True)
    assert not result.empty_values


def test_unknown_keys_flagged_when_optional_provided(base_env):
    result = validate(
        base_env,
        required=["DATABASE_URL", "SECRET_KEY"],
        optional=["DEBUG"],
    )
    assert result.is_valid
    assert not result.unknown_keys


def test_extra_key_flagged_as_unknown(base_env):
    result = validate(
        base_env,
        required=["DATABASE_URL", "SECRET_KEY"],
        optional=[],  # DEBUG not listed
    )
    assert "DEBUG" in result.unknown_keys
    assert not result.is_valid


def test_unknown_keys_not_checked_when_optional_is_none(base_env):
    result = validate(
        base_env,
        required=["DATABASE_URL"],
        optional=None,
    )
    assert not result.unknown_keys
    assert result.is_valid


def test_summary_all_clear():
    result = ValidationResult()
    assert result.summary() == "All checks passed."


def test_summary_lists_violations():
    result = ValidationResult(
        missing_required={"API_KEY"},
        empty_values={"SECRET_KEY"},
        unknown_keys={"TYPO_VAR"},
    )
    summary = result.summary()
    assert "MISSING (required): API_KEY" in summary
    assert "EMPTY VALUE:        SECRET_KEY" in summary
    assert "UNKNOWN KEY:        TYPO_VAR" in summary
