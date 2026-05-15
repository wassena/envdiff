"""Tests for envdiff.pinner."""
from __future__ import annotations

import pytest

from envdiff.pinner import (
    PinResult,
    pin_string,
    pin_values,
    pinned_count,
    to_env_string,
)


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_pin_values_updates_existing_key():
    result = pin_values(BASE, {"DEBUG": "false"})
    assert result.values["DEBUG"] == "false"


def test_pin_values_records_pinned_key():
    result = pin_values(BASE, {"DEBUG": "false"})
    assert "DEBUG" in result.pinned


def test_pin_values_unchanged_key_not_recorded():
    result = pin_values(BASE, {"HOST": "localhost"})
    assert "HOST" not in result.pinned


def test_pin_values_adds_missing_key_by_default():
    result = pin_values(BASE, {"NEW_KEY": "hello"})
    assert result.values["NEW_KEY"] == "hello"
    assert "NEW_KEY" in result.pinned


def test_pin_values_no_add_skips_missing_key():
    result = pin_values(BASE, {"NEW_KEY": "hello"}, add_missing=False)
    assert "NEW_KEY" not in result.values
    assert "NEW_KEY" in result.skipped


def test_pin_values_preserves_unaffected_keys():
    result = pin_values(BASE, {"PORT": "9999"})
    assert result.values["HOST"] == "localhost"
    assert result.values["DEBUG"] == "true"


def test_pinned_count_reflects_changes():
    result = pin_values(BASE, {"PORT": "9999", "DEBUG": "false"})
    assert pinned_count(result) == 2


def test_pinned_count_zero_when_no_changes():
    result = pin_values(BASE, {"HOST": "localhost"})
    assert pinned_count(result) == 0


def test_pin_string_parses_and_pins():
    source = "HOST=localhost\nPORT=5432\n"
    result = pin_string(source, {"PORT": "3306"})
    assert result.values["PORT"] == "3306"
    assert "PORT" in result.pinned


def test_pin_string_no_add_skips_absent_key():
    source = "HOST=localhost\n"
    result = pin_string(source, {"MISSING": "x"}, add_missing=False)
    assert "MISSING" not in result.values
    assert "MISSING" in result.skipped


def test_to_env_string_format():
    result = PinResult(values={"A": "1", "B": "2"})
    output = to_env_string(result)
    assert "A=1" in output
    assert "B=2" in output


def test_multiple_pins_applied():
    result = pin_values(BASE, {"HOST": "prod.db", "PORT": "5433", "DEBUG": "false"})
    assert result.values["HOST"] == "prod.db"
    assert result.values["PORT"] == "5433"
    assert result.values["DEBUG"] == "false"
    assert pinned_count(result) == 3
