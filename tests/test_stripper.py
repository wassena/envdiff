"""Tests for envdiff.stripper."""
import pytest

from envdiff.stripper import (
    StripResult,
    strip_keys,
    strip_string,
    stripped_count,
    to_env_string,
)

SAMPLE = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc\nAPP_NAME=myapp\n"


def test_strip_explicit_key_removes_it():
    result = strip_string(SAMPLE, keys=["DB_PORT"])
    assert "DB_PORT" not in result.values
    assert "DB_HOST" in result.values


def test_strip_records_stripped_keys():
    result = strip_string(SAMPLE, keys=["DB_PORT", "APP_NAME"])
    assert sorted(result.stripped) == ["APP_NAME", "DB_PORT"]


def test_strip_pattern_removes_matching():
    result = strip_string(SAMPLE, patterns=[r"^DB_"])
    assert "DB_HOST" not in result.values
    assert "DB_PORT" not in result.values
    assert "SECRET_KEY" in result.values


def test_strip_pattern_records_stripped():
    result = strip_string(SAMPLE, patterns=[r"^DB_"])
    assert set(result.stripped) == {"DB_HOST", "DB_PORT"}


def test_strip_no_criteria_returns_all():
    result = strip_string(SAMPLE)
    assert len(result.values) == 4
    assert result.stripped == []


def test_strip_combined_keys_and_patterns():
    result = strip_string(SAMPLE, keys=["APP_NAME"], patterns=[r"SECRET"])
    assert "APP_NAME" not in result.values
    assert "SECRET_KEY" not in result.values
    assert "DB_HOST" in result.values


def test_stripped_count_helper():
    result = strip_string(SAMPLE, keys=["DB_HOST", "DB_PORT"])
    assert stripped_count(result) == 2


def test_to_env_string_format():
    result = strip_string(SAMPLE, keys=["SECRET_KEY", "APP_NAME"])
    output = to_env_string(result)
    assert "DB_HOST=localhost" in output
    assert "SECRET_KEY" not in output


def test_strip_nonexistent_key_is_ignored():
    result = strip_string(SAMPLE, keys=["DOES_NOT_EXIST"])
    assert len(result.values) == 4
    assert result.stripped == []


def test_strip_keys_dict_input():
    values = {"A": "1", "B": "2", "C": "3"}
    result = strip_keys(values, keys=["B"])
    assert result.values == {"A": "1", "C": "3"}
    assert result.stripped == ["B"]
