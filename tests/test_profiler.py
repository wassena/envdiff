"""Tests for envdiff.profiler."""
import textwrap

import pytest

from envdiff.profiler import profile_string, ProfileResult


SAMPLE = textwrap.dedent("""\
    APP_NAME=myapp
    APP_ENV=production
    APP_DEBUG=
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=mydb
    SECRET_KEY=supersecret
    # a comment
    EMPTY_VAL=
""")


@pytest.fixture
def result() -> ProfileResult:
    return profile_string(SAMPLE)


def test_total_keys(result):
    assert result.total_keys == 7


def test_empty_keys_detected(result):
    assert "APP_DEBUG" in result.empty_keys
    assert "EMPTY_VAL" in result.empty_keys


def test_empty_count(result):
    assert result.empty_count == 2


def test_non_empty_key_not_in_empty(result):
    assert "APP_NAME" not in result.empty_keys


def test_longest_key(result):
    assert result.longest_key == "SECRET_KEY"


def test_longest_value_key(result):
    assert result.longest_value_key == "SECRET_KEY"


def test_prefixes_detected(result):
    assert "APP" in result.prefixes
    assert "DB" in result.prefixes


def test_prefix_counts(result):
    assert result.prefixes["APP"] == 3
    assert result.prefixes["DB"] == 3


def test_prefix_count_property(result):
    assert result.prefix_count == 3  # APP, DB, SECRET


def test_no_duplicates_in_clean_input(result):
    assert result.duplicate_keys == []


def test_duplicate_keys_detected():
    raw = "FOO=bar\nFOO=baz\nBAR=1\n"
    r = profile_string(raw)
    assert "FOO" in r.duplicate_keys
    assert "BAR" not in r.duplicate_keys


def test_values_dict_populated(result):
    assert result.values["APP_NAME"] == "myapp"
    assert result.values["DB_PORT"] == "5432"


def test_empty_input():
    r = profile_string("")
    assert r.total_keys == 0
    assert r.empty_keys == []
    assert r.prefixes == {}
    assert r.longest_key == ""


def test_custom_separator():
    raw = "NS.KEY1=a\nNS.KEY2=b\nOTHER=c\n"
    r = profile_string(raw, separator=".")
    assert "NS" in r.prefixes
    assert r.prefixes["NS"] == 2
