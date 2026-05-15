"""Tests for envdiff.rotator."""
import pytest

from envdiff.rotator import (
    RotateResult,
    deprecated_count,
    rotate_keys,
    rotate_string,
    rotated_count,
    to_env_string,
)


SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_rotate_single_key():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.values
    assert result.values["DATABASE_HOST"] == "localhost"


def test_original_key_removed_by_default():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" not in result.values


def test_rotated_list_records_old_key():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.rotated


def test_unaffected_keys_preserved():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert result.values["DB_PORT"] == "5432"
    assert result.values["SECRET"] == "abc"


def test_missing_key_goes_to_skipped():
    result = rotate_keys(SAMPLE, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.values


def test_keep_old_preserves_original_key():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"}, keep_old=True)
    assert "DB_HOST" in result.values
    assert "DATABASE_HOST" in result.values


def test_keep_old_records_deprecated():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"}, keep_old=True)
    assert "DB_HOST" in result.deprecated


def test_rotated_count():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert rotated_count(result) == 2


def test_deprecated_count_without_keep_old():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert deprecated_count(result) == 0


def test_deprecated_count_with_keep_old():
    result = rotate_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"}, keep_old=True)
    assert deprecated_count(result) == 1


def test_rotate_string_parses_source():
    source = "DB_HOST=localhost\nDB_PORT=5432\n"
    result = rotate_string(source, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.values
    assert result.values["DATABASE_HOST"] == "localhost"


def test_to_env_string_format():
    result = RotateResult(values={"A": "1", "B": "2"})
    env_str = to_env_string(result)
    assert "A=1" in env_str
    assert "B=2" in env_str


def test_multiple_renames():
    result = rotate_keys(
        SAMPLE,
        {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"},
    )
    assert "DATABASE_HOST" in result.values
    assert "DATABASE_PORT" in result.values
    assert "DB_HOST" not in result.values
    assert "DB_PORT" not in result.values
