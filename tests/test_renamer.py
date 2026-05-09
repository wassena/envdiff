"""Tests for envdiff.renamer."""
import pytest

from envdiff.renamer import (
    RenameResult,
    rename_keys,
    rename_in_string,
    to_env_string,
)


SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_rename_single_key():
    result = rename_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_rename_preserves_value():
    result = rename_keys(SAMPLE, {"DB_PORT": "DATABASE_PORT"})
    assert result.env["DATABASE_PORT"] == "5432"


def test_rename_records_renamed_keys():
    result = rename_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert result.renamed == {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    assert result.rename_count == 2


def test_rename_untouched_keys_preserved():
    result = rename_keys(SAMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert result.env["DB_PORT"] == "5432"
    assert result.env["APP_ENV"] == "production"


def test_missing_key_recorded_in_skipped():
    result = rename_keys(SAMPLE, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert result.rename_count == 0


def test_missing_key_ignored_when_flag_set():
    result = rename_keys(SAMPLE, {"MISSING_KEY": "NEW_KEY"}, ignore_missing=True)
    assert result.skipped == []


def test_rename_in_string_basic():
    env_str = "DB_HOST=localhost\nDB_PORT=5432\n"
    result = rename_in_string(env_str, {"DB_HOST": "DATABASE_HOST"})
    assert result.env["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in result.env


def test_rename_in_string_missing_key():
    env_str = "APP_ENV=staging\n"
    result = rename_in_string(env_str, {"NONEXISTENT": "OTHER"})
    assert "NONEXISTENT" in result.skipped


def test_to_env_string_output():
    result = rename_keys({"FOO": "bar", "BAZ": "qux"}, {"FOO": "FOOD"})
    output = to_env_string(result)
    assert "FOOD=bar" in output
    assert "BAZ=qux" in output
    assert output.endswith("\n")


def test_to_env_string_no_renames():
    result = rename_keys({"X": "1", "Y": "2"}, {})
    output = to_env_string(result)
    assert "X=1" in output
    assert "Y=2" in output


def test_rename_result_defaults():
    r = RenameResult()
    assert r.renamed == {}
    assert r.skipped == []
    assert r.env == {}
    assert r.rename_count == 0


def test_rename_multiple_missing_keys_all_recorded():
    """All missing keys should appear in skipped, not just the first one."""
    result = rename_keys(SAMPLE, {"MISSING_ONE": "NEW_ONE", "MISSING_TWO": "NEW_TWO"})
    assert "MISSING_ONE" in result.skipped
    assert "MISSING_TWO" in result.skipped
    assert result.rename_count == 0
