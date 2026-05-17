"""Tests for envdiff.aliaser."""
from envdiff.aliaser import (
    AliasResult,
    alias_count,
    alias_string,
    alias_values,
    to_env_string,
)


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_alias_adds_new_key():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.values
    assert result.values["DATABASE_HOST"] == "localhost"


def test_alias_keeps_original_by_default():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.values


def test_alias_removes_original_when_requested():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST"}, keep_original=False)
    assert "DB_HOST" not in result.values
    assert "DATABASE_HOST" in result.values


def test_alias_records_aliased_key():
    result = alias_values(BASE, {"DB_PORT": "DATABASE_PORT"})
    assert "DATABASE_PORT" in result.aliased


def test_missing_source_key_goes_to_skipped():
    result = alias_values(BASE, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.values


def test_unrelated_keys_preserved():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST"})
    assert result.values["APP_ENV"] == "production"
    assert result.values["DB_PORT"] == "5432"


def test_alias_count_matches_aliased_list():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert alias_count(result) == 2


def test_alias_string_parses_and_aliases():
    text = "FOO=bar\nBAZ=qux\n"
    result = alias_string(text, {"FOO": "FOO_ALIAS"})
    assert result.values["FOO_ALIAS"] == "bar"
    assert result.values["FOO"] == "bar"


def test_alias_string_keep_original_false():
    text = "FOO=bar\nBAZ=qux\n"
    result = alias_string(text, {"FOO": "FOO_ALIAS"}, keep_original=False)
    assert "FOO" not in result.values
    assert result.values["FOO_ALIAS"] == "bar"


def test_to_env_string_contains_all_keys():
    result = alias_values(BASE, {"DB_HOST": "DATABASE_HOST"})
    output = to_env_string(result)
    assert "DATABASE_HOST=localhost" in output
    assert "DB_HOST=localhost" in output
    assert "APP_ENV=production" in output


def test_multiple_aliases_from_same_source():
    # Two different source keys aliased independently
    result = alias_values(
        BASE,
        {"DB_HOST": "HOST_ALIAS", "APP_ENV": "ENVIRONMENT"},
        keep_original=False,
    )
    assert "HOST_ALIAS" in result.values
    assert "ENVIRONMENT" in result.values
    assert "DB_HOST" not in result.values
    assert "APP_ENV" not in result.values
    assert alias_count(result) == 2
