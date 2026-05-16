"""Tests for envdiff.sanitizer."""
from __future__ import annotations

import pytest

from envdiff.sanitizer import (
    SanitizeResult,
    sanitize_string,
    sanitize_values,
    sanitized_count,
    to_env_string,
)


def test_sanitize_values_removes_control_chars():
    env = {"KEY": "hello\x00world"}
    result = sanitize_values(env)
    assert result.values["KEY"] == "helloworld"
    assert "KEY" in result.sanitized


def test_sanitize_values_strips_leading_trailing_whitespace():
    env = {"KEY": "  value  "}
    result = sanitize_values(env)
    assert result.values["KEY"] == "value"
    assert "KEY" in result.sanitized


def test_sanitize_values_no_strip_whitespace_preserves_spaces():
    env = {"KEY": "  value  "}
    result = sanitize_values(env, strip_whitespace=False)
    assert result.values["KEY"] == "  value  "
    assert "KEY" not in result.sanitized


def test_clean_value_not_recorded():
    env = {"KEY": "clean_value"}
    result = sanitize_values(env)
    assert result.sanitized == []


def test_sanitized_count_reflects_changed_keys():
    env = {"A": "ok", "B": "bad\x01", "C": "also\x1fbad"}
    result = sanitize_values(env)
    assert sanitized_count(result) == 2


def test_sanitize_string_parses_dotenv_text():
    text = "FOO=bar\nBAZ=qux\n"
    result = sanitize_string(text)
    assert result.values == {"FOO": "bar", "BAZ": "qux"}
    assert result.sanitized == []


def test_sanitize_string_with_control_char_in_value():
    text = "TOKEN=abc\x07def\n"
    result = sanitize_string(text)
    assert result.values["TOKEN"] == "abcdef"
    assert "TOKEN" in result.sanitized


def test_to_env_string_roundtrip():
    env = {"A": "1", "B": "2"}
    result = sanitize_values(env)
    output = to_env_string(result)
    assert "A=1" in output
    assert "B=2" in output


def test_to_env_string_empty():
    result = SanitizeResult(values={})
    assert to_env_string(result) == ""


def test_multiple_control_chars_all_stripped():
    env = {"KEY": "\x00a\x01b\x1fc"}
    result = sanitize_values(env)
    assert result.values["KEY"] == "abc"


def test_tab_not_stripped_as_control_char():
    """Tabs (\x09) are NOT in the stripped range and should be preserved."""
    env = {"KEY": "val\tue"}
    result = sanitize_values(env)
    assert result.values["KEY"] == "val\tue"
    assert "KEY" not in result.sanitized
