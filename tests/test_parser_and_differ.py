"""Tests for envdiff.parser and envdiff.differ."""

import pytest

from envdiff.parser import parse_env_string
from envdiff.differ import diff_envs, DiffResult


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

SAMPLE_ENV = """
# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME="myapp"
DB_PASSWORD='s3cr3t'

# App
DEBUG=true
SECRET_KEY=abc123
"""


def test_parse_basic():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_strips_double_quotes():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_NAME"] == "myapp"


def test_parse_strips_single_quotes():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_PASSWORD"] == "s3cr3t"


def test_parse_ignores_comments_and_blanks():
    result = parse_env_string(SAMPLE_ENV)
    assert len(result) == 5


def test_parse_malformed_line_raises():
    bad_content = "VALID=ok\nNOT VALID LINE\n"
    with pytest.raises(ValueError, match="malformed line"):
        parse_env_string(bad_content)


def test_parse_empty_value():
    result = parse_env_string("EMPTY=\n")
    assert result["EMPTY"] == ""


# ---------------------------------------------------------------------------
# Differ tests
# ---------------------------------------------------------------------------


def test_diff_identical():
    env = {"A": "1", "B": "2"}
    result = diff_envs(env, env.copy())
    assert not result.has_differences
    assert sorted(result.identical) == ["A", "B"]


def test_diff_missing_in_target():
    source = {"A": "1", "B": "2"}
    target = {"A": "1"}
    result = diff_envs(source, target)
    assert result.missing_in_target == ["B"]
    assert not result.missing_in_source


def test_diff_missing_in_source():
    source = {"A": "1"}
    target = {"A": "1", "EXTRA": "x"}
    result = diff_envs(source, target)
    assert result.missing_in_source == ["EXTRA"]


def test_diff_changed_values():
    source = {"HOST": "localhost", "PORT": "5432"}
    target = {"HOST": "prod.db", "PORT": "5432"}
    result = diff_envs(source, target)
    assert "HOST" in result.changed
    assert result.changed["HOST"] == ("localhost", "prod.db")
    assert "PORT" not in result.changed


def test_diff_has_differences_flag():
    result = DiffResult(missing_in_target=["X"])
    assert result.has_differences

    empty = DiffResult()
    assert not empty.has_differences
