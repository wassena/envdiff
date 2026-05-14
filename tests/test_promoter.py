"""Tests for envdiff.promoter."""

import pytest

from envdiff.promoter import (
    PromoteResult,
    promote,
    promote_strings,
    promoted_count,
    overwrite_count,
    to_env_string,
)


SOURCE = {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"}
TARGET = {"DB_HOST": "local-db", "APP_ENV": "staging"}


# ---------------------------------------------------------------------------
# promote() core behaviour
# ---------------------------------------------------------------------------

def test_promote_all_keys_by_default():
    result = promote(SOURCE, TARGET)
    assert "DB_HOST" in result.promoted
    assert "DB_PORT" in result.promoted
    assert "SECRET" in result.promoted


def test_promote_records_overwritten_key():
    result = promote(SOURCE, TARGET)
    assert "DB_HOST" in result.overwritten


def test_promote_does_not_touch_target_only_keys():
    result = promote(SOURCE, TARGET)
    # APP_ENV exists only in target — it should remain in base, not skipped
    assert "APP_ENV" not in result.skipped
    assert result.base["APP_ENV"] == "staging"


def test_promote_filtered_keys_only():
    result = promote(SOURCE, TARGET, keys=["DB_HOST"])
    assert list(result.promoted.keys()) == ["DB_HOST"]


def test_promote_missing_key_in_source_goes_to_skipped():
    result = promote(SOURCE, TARGET, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped
    assert "NONEXISTENT" not in result.promoted


def test_promote_overwrite_false_skips_existing_target_key():
    result = promote(SOURCE, TARGET, overwrite=False)
    # DB_HOST exists in target — should be skipped, not promoted
    assert "DB_HOST" in result.skipped
    assert "DB_HOST" not in result.promoted


def test_promote_overwrite_false_still_adds_new_keys():
    result = promote(SOURCE, TARGET, overwrite=False)
    assert "DB_PORT" in result.promoted
    assert "SECRET" in result.promoted


# ---------------------------------------------------------------------------
# helper functions
# ---------------------------------------------------------------------------

def test_promoted_count():
    result = promote(SOURCE, TARGET)
    assert promoted_count(result) == len(result.promoted)


def test_overwrite_count():
    result = promote(SOURCE, TARGET)
    assert overwrite_count(result) == len(result.overwritten)


def test_to_env_string_contains_all_keys():
    result = promote(SOURCE, TARGET)
    env_str = to_env_string(result)
    for key in {**TARGET, **SOURCE}:
        assert key in env_str


def test_to_env_string_promoted_value_wins():
    result = promote(SOURCE, TARGET)
    env_str = to_env_string(result)
    assert "DB_HOST=prod-db" in env_str


# ---------------------------------------------------------------------------
# promote_strings convenience wrapper
# ---------------------------------------------------------------------------

def test_promote_strings_basic():
    src = "API_URL=https://prod.example.com\nTOKEN=abc123\n"
    tgt = "API_URL=https://staging.example.com\nDEBUG=true\n"
    result = promote_strings(src, tgt)
    assert result.promoted["API_URL"] == "https://prod.example.com"
    assert result.promoted["TOKEN"] == "abc123"


def test_promote_strings_preserves_target_only_key_in_base():
    src = "FOO=bar\n"
    tgt = "FOO=old\nONLY_HERE=1\n"
    result = promote_strings(src, tgt)
    assert result.base["ONLY_HERE"] == "1"
