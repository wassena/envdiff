"""Tests for envdiff.trimmer."""
from __future__ import annotations

import pytest

from envdiff.trimmer import (
    TrimResult,
    trim_values,
    trim_string,
    to_env_string,
    trimmed_count,
)


# ---------------------------------------------------------------------------
# trim_values
# ---------------------------------------------------------------------------

def test_trim_values_strips_value_whitespace():
    env = {"KEY": "  hello  ", "OTHER": "world"}
    result = trim_values(env)
    assert result.values["KEY"] == "hello"
    assert result.values["OTHER"] == "world"


def test_trim_values_records_changed_value_key():
    env = {"KEY": "  hello  "}
    result = trim_values(env)
    assert "KEY" in result.trimmed_values


def test_trim_values_unchanged_value_not_recorded():
    env = {"KEY": "hello"}
    result = trim_values(env)
    assert "KEY" not in result.trimmed_values


def test_trim_keys_strips_key_whitespace():
    env = {"  KEY  ": "value"}
    result = trim_values(env, trim_keys=True)
    assert "KEY" in result.values
    assert "  KEY  " not in result.values


def test_trim_keys_records_changed_key():
    env = {"  KEY  ": "value"}
    result = trim_values(env, trim_keys=True)
    assert "  KEY  " in result.trimmed_keys


def test_trim_keys_disabled_preserves_key_whitespace():
    env = {"  KEY  ": "value"}
    result = trim_values(env, trim_keys=False)
    assert "  KEY  " in result.values
    assert result.trimmed_keys == []


def test_no_trim_values_preserves_value_whitespace():
    env = {"KEY": "  hello  "}
    result = trim_values(env, trim_values=False)
    assert result.values["KEY"] == "  hello  "
    assert result.trimmed_values == []


def test_trimmed_count_reflects_unique_changed_entries():
    env = {"A": "  x  ", "B": "clean"}
    result = trim_values(env)
    assert trimmed_count(result) == 1


def test_trimmed_count_zero_when_nothing_changed():
    env = {"A": "x", "B": "y"}
    result = trim_values(env)
    assert trimmed_count(result) == 0


# ---------------------------------------------------------------------------
# trim_string
# ---------------------------------------------------------------------------

def test_trim_string_parses_and_trims():
    text = "KEY=  spaced  \nOTHER=clean"
    result = trim_string(text)
    assert result.values["KEY"] == "spaced"
    assert result.values["OTHER"] == "clean"


def test_trim_string_trim_keys_option():
    # Parser will strip surrounding whitespace in key names if present
    text = "MYKEY=  value  "
    result = trim_string(text, trim_keys=True)
    assert "MYKEY" in result.values


# ---------------------------------------------------------------------------
# to_env_string
# ---------------------------------------------------------------------------

def test_to_env_string_produces_dotenv_lines():
    result = TrimResult(values={"A": "1", "B": "2"})
    output = to_env_string(result)
    assert "A=1" in output
    assert "B=2" in output


def test_to_env_string_roundtrip():
    from envdiff.parser import parse_env_string

    env = {"FOO": "bar", "BAZ": "qux"}
    result = trim_values(env)
    parsed_back = parse_env_string(to_env_string(result))
    assert parsed_back == env
