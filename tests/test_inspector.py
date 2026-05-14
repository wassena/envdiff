"""Tests for envdiff.inspector and envdiff.cli_inspect."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from envdiff.inspector import inspect_string, inspect_values, InspectResult


SAMPLE = textwrap.dedent("""\
    APP_NAME=myapp
    APP_VERSION=1.2.3
    APP_DEBUG=true
    APP_EMPTY=
    DB_HOST=localhost
    DB_PORT=5432
    DB_URL=https://db.example.com/mydb
    SECRET_KEY=supersecret
    LONG_VALUE={}
""".format("x" * 90))


@pytest.fixture
def result() -> InspectResult:
    return inspect_string(SAMPLE)


def test_total_keys(result):
    assert result.total_keys == 9


def test_empty_values_detected(result):
    assert "APP_EMPTY" in result.empty_values
    assert result.empty_count == 1


def test_numeric_values_detected(result):
    assert "DB_PORT" in result.numeric_values
    assert "APP_VERSION" not in result.numeric_values  # semver, not plain numeric


def test_boolean_values_detected(result):
    assert "APP_DEBUG" in result.boolean_values


def test_url_values_detected(result):
    assert "DB_URL" in result.url_values


def test_long_values_detected(result):
    assert "LONG_VALUE" in result.long_values


def test_prefix_grouping(result):
    assert result.prefixes["APP"] == 4
    assert result.prefixes["DB"] == 3
    assert result.unique_prefixes >= 2


def test_key_lengths_populated(result):
    assert result.key_lengths["APP_NAME"] == len("myapp")
    assert result.key_lengths["APP_EMPTY"] == 0


def test_empty_env_returns_zero_totals():
    r = inspect_string("")
    assert r.total_keys == 0
    assert r.empty_count == 0
    assert r.unique_prefixes == 0


def test_custom_separator():
    r = inspect_string("APP-NAME=foo\nAPP-DEBUG=true", separator="-")
    assert r.prefixes.get("APP", 0) == 2


def test_inspect_file_not_found():
    from envdiff.cli_inspect import run, build_parser
    parser = build_parser()
    args = parser.parse_args(["nonexistent.env"])
    assert run(args) == 2


def test_cli_text_output(tmp_path):
    from envdiff.cli_inspect import run, build_parser
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=foo\nDB_PORT=5432\n")
    parser = build_parser()
    args = parser.parse_args([str(env_file)])
    assert run(args) == 0


def test_cli_json_output(tmp_path, capsys):
    from envdiff.cli_inspect import run, build_parser
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=foo\nDB_PORT=5432\n")
    parser = build_parser()
    args = parser.parse_args([str(env_file), "--format", "json"])
    assert run(args) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_keys"] == 2
    assert "DB_PORT" in data["numeric_values"]
