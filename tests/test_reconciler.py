"""Tests for envdiff.reconciler."""

import pytest
from envdiff.differ import diff_envs
from envdiff.reconciler import reconcile, to_env_string


BASE = {"HOST": "localhost", "PORT": "5432", "EXTRA": "yes"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


@pytest.fixture
def diff():
    return diff_envs(BASE, TARGET)


def test_fill_missing_adds_new_keys(diff):
    result = reconcile(BASE, TARGET, diff, strategy="fill_missing")
    assert result["SECRET"] == "abc123"
    assert result["HOST"] == "localhost"  # unchanged
    assert result["EXTRA"] == "yes"       # kept


def test_fill_missing_with_placeholder(diff):
    result = reconcile(BASE, TARGET, diff, strategy="fill_missing", placeholder="CHANGEME")
    assert result["SECRET"] == "CHANGEME"


def test_overwrite_updates_changed_keys(diff):
    result = reconcile(BASE, TARGET, diff, strategy="overwrite")
    assert result["HOST"] == "prod.example.com"
    assert result["SECRET"] not in result  # overwrite doesn't add missing
    assert result["EXTRA"] == "yes"


def test_prune_extra_removes_keys_absent_in_target(diff):
    result = reconcile(BASE, TARGET, diff, strategy="prune_extra")
    assert "EXTRA" not in result
    assert "HOST" in result  # kept
    assert "PORT" in result


def test_full_sync(diff):
    result = reconcile(BASE, TARGET, diff, strategy="full_sync")
    assert result["HOST"] == "prod.example.com"  # overwritten
    assert result["SECRET"] == "abc123"          # filled
    assert "EXTRA" not in result                 # pruned


def test_invalid_strategy_raises(diff):
    with pytest.raises(ValueError, match="Unknown reconcile strategy"):
        reconcile(BASE, TARGET, diff, strategy="magic")


def test_to_env_string_basic():
    env = {"FOO": "bar", "BAZ": "qux"}
    output = to_env_string(env)
    assert "FOO=bar" in output
    assert "BAZ=qux" in output


def test_to_env_string_quotes_spaces():
    env = {"MSG": "hello world"}
    output = to_env_string(env)
    assert 'MSG="hello world"' in output


def test_to_env_string_quotes_empty_value():
    env = {"EMPTY": ""}
    output = to_env_string(env)
    assert 'EMPTY=""' in output


def test_to_env_string_ends_with_newline():
    env = {"A": "1"}
    assert to_env_string(env).endswith("\n")


def test_to_env_string_empty_dict():
    assert to_env_string({}) == ""
