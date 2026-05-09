"""Tests for envdiff.redactor."""
from __future__ import annotations

import pytest

from envdiff.redactor import (
    RedactResult,
    _redact_value,
    redact_values,
    redact_string,
    DEFAULT_REDACT_CHAR,
    DEFAULT_REDACT_LENGTH,
)


SAMPLE: dict[str, str] = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123xyz",
    "DEBUG": "true",
}


def test_redact_value_default():
    assert _redact_value("secret") == "*" * DEFAULT_REDACT_LENGTH


def test_redact_value_custom_char_and_length():
    assert _redact_value("secret", char="#", length=4) == "####"


def test_redact_value_partial_long_value():
    result = _redact_value("abcdefgh", partial=True)
    assert result.startswith("ab")
    assert result.endswith("gh")
    assert "*" in result


def test_redact_value_partial_short_value():
    # Short values fall back to full redaction
    result = _redact_value("ab", partial=True)
    assert result == "*" * DEFAULT_REDACT_LENGTH


def test_redact_values_all_keys_by_default():
    result = redact_values(SAMPLE)
    assert result.redact_count == len(SAMPLE)
    for v in result.redacted.values():
        assert v == "*" * DEFAULT_REDACT_LENGTH


def test_redact_values_specific_keys():
    result = redact_values(SAMPLE, keys=["DB_PASSWORD", "API_KEY"])
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted["DB_PASSWORD"] == "*" * DEFAULT_REDACT_LENGTH
    assert result.redacted["API_KEY"] == "*" * DEFAULT_REDACT_LENGTH


def test_redact_values_records_redacted_keys():
    result = redact_values(SAMPLE, keys=["DB_PASSWORD"])
    assert "DB_PASSWORD" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_redact_values_preserves_key_order():
    result = redact_values(SAMPLE)
    assert list(result.redacted.keys()) == list(SAMPLE.keys())


def test_redact_values_missing_key_ignored():
    result = redact_values(SAMPLE, keys=["NONEXISTENT"])
    assert result.redact_count == 0
    assert result.redacted == SAMPLE


def test_redact_string_parses_and_redacts():
    env_str = "DB_PASSWORD=secret\nAPP_NAME=myapp\n"
    result = redact_string(env_str, keys=["DB_PASSWORD"])
    assert result.redacted["DB_PASSWORD"] == "*" * DEFAULT_REDACT_LENGTH
    assert result.redacted["APP_NAME"] == "myapp"


def test_redact_string_no_keys_redacts_all():
    env_str = "FOO=bar\nBAZ=qux\n"
    result = redact_string(env_str)
    assert all(v == "*" * DEFAULT_REDACT_LENGTH for v in result.redacted.values())


def test_redact_result_original_keys():
    result = redact_values(SAMPLE)
    assert result.original_keys == list(SAMPLE.keys())
