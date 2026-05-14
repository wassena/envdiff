"""Tests for envdiff.filter."""

import pytest

from envdiff.filter import FilterResult, filter_keys, filter_string, to_env_string


SAMPLE = "DB_HOST=localhost\nDB_PASS=secret\nAPP_ENV=prod\nTEST_FLAG=1\n"


# ---------------------------------------------------------------------------
# filter_keys
# ---------------------------------------------------------------------------

def test_filter_keys_removes_explicit_key():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret", "APP_ENV": "prod"}
    result = filter_keys(env, keys=["DB_PASS"])
    assert "DB_PASS" not in result.kept
    assert result.removed == {"DB_PASS": "secret"}


def test_filter_keys_removes_pattern_match():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret", "APP_ENV": "prod"}
    result = filter_keys(env, patterns=["^DB_"])
    assert "DB_HOST" not in result.kept
    assert "DB_PASS" not in result.kept
    assert "APP_ENV" in result.kept


def test_filter_keys_invert_keeps_only_matched():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret", "APP_ENV": "prod"}
    result = filter_keys(env, keys=["APP_ENV"], invert=True)
    assert result.kept == {"APP_ENV": "prod"}
    assert "DB_HOST" in result.removed


def test_filter_keys_no_criteria_returns_all():
    env = {"A": "1", "B": "2"}
    result = filter_keys(env)
    assert result.kept == env
    assert result.removed == {}


def test_filter_keys_combined_keys_and_patterns():
    env = {"DB_HOST": "h", "SECRET": "s", "APP_ENV": "prod", "TEST_X": "1"}
    result = filter_keys(env, keys=["SECRET"], patterns=["^TEST_"])
    assert "SECRET" not in result.kept
    assert "TEST_X" not in result.kept
    assert "DB_HOST" in result.kept
    assert result.removed_count == 2


def test_filter_keys_counts():
    env = {"A": "1", "B": "2", "C": "3"}
    result = filter_keys(env, keys=["A", "B"])
    assert result.kept_count == 1
    assert result.removed_count == 2


# ---------------------------------------------------------------------------
# filter_string
# ---------------------------------------------------------------------------

def test_filter_string_removes_key():
    result = filter_string(SAMPLE, keys=["DB_PASS"])
    assert "DB_PASS" not in result.kept


def test_filter_string_pattern():
    result = filter_string(SAMPLE, patterns=["^TEST_"])
    assert "TEST_FLAG" not in result.kept
    assert "APP_ENV" in result.kept


def test_filter_string_invert():
    result = filter_string(SAMPLE, patterns=["^DB_"], invert=True)
    assert set(result.kept.keys()) == {"DB_HOST", "DB_PASS"}


# ---------------------------------------------------------------------------
# to_env_string
# ---------------------------------------------------------------------------

def test_to_env_string_format():
    result = FilterResult(kept={"A": "1", "B": "2"}, removed={})
    text = to_env_string(result)
    assert "A=1\n" in text
    assert "B=2\n" in text


def test_to_env_string_empty_kept():
    result = FilterResult(kept={}, removed={"X": "y"})
    assert to_env_string(result) == ""
