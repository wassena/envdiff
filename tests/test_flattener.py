"""Tests for envdiff.flattener."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.flattener import (
    FlattenResult,
    collapsed_count,
    expand_keys,
    expand_string,
    expanded_count,
    flatten_keys,
    flatten_string,
)


# ---------------------------------------------------------------------------
# flatten_keys
# ---------------------------------------------------------------------------

def test_flatten_keys_collapses_separator():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432", "APP_ENV": "prod"}
    result = flatten_keys(env, separator="__")
    assert "db.host" in result.values
    assert "db.port" in result.values
    assert result.values["db.host"] == "localhost"


def test_flatten_keys_leaves_plain_keys_intact():
    env = {"APP_ENV": "prod", "DEBUG": "true"}
    result = flatten_keys(env)
    assert result.values == {"APP_ENV": "prod", "DEBUG": "true"}


def test_flatten_keys_records_collapsed():
    env = {"DB__HOST": "localhost", "PLAIN": "val"}
    result = flatten_keys(env)
    assert "DB__HOST" in result.collapsed_keys
    assert "PLAIN" not in result.collapsed_keys


def test_flatten_keys_records_expanded():
    env = {"DB__HOST": "localhost", "PLAIN": "val"}
    result = flatten_keys(env)
    assert "PLAIN" in result.expanded_keys


def test_collapsed_count():
    env = {"A__B": "1", "A__C": "2", "X": "3"}
    result = flatten_keys(env)
    assert collapsed_count(result) == 2


def test_expanded_count():
    env = {"A__B": "1", "X": "3", "Y": "4"}
    result = flatten_keys(env)
    assert expanded_count(result) == 2


def test_flatten_keys_custom_separator():
    env = {"DB_HOST": "localhost"}
    result = flatten_keys(env, separator="_")
    assert "db.host" in result.values


# ---------------------------------------------------------------------------
# expand_keys
# ---------------------------------------------------------------------------

def test_expand_keys_restores_separator():
    env = {"db.host": "localhost", "db.port": "5432"}
    result = expand_keys(env, separator="__")
    assert "DB__HOST" in result.values
    assert "DB__PORT" in result.values


def test_expand_keys_leaves_non_dotted_intact():
    env = {"APP_ENV": "prod"}
    result = expand_keys(env)
    assert result.values == {"APP_ENV": "prod"}


def test_expand_keys_records_expanded():
    env = {"db.host": "localhost", "PLAIN": "val"}
    result = expand_keys(env)
    assert "DB__HOST" in result.expanded_keys


# ---------------------------------------------------------------------------
# roundtrip
# ---------------------------------------------------------------------------

def test_flatten_expand_roundtrip():
    original = {"DB__HOST": "localhost", "DB__PORT": "5432", "APP_ENV": "prod"}
    flattened = flatten_keys(original)
    restored = expand_keys(flattened.values)
    assert restored.values == original


# ---------------------------------------------------------------------------
# string helpers
# ---------------------------------------------------------------------------

def test_flatten_string_parses_and_flattens():
    src = "DB__HOST=localhost\nDB__PORT=5432\n"
    result = flatten_string(src)
    assert "db.host" in result.values


def test_expand_string_parses_and_expands():
    src = "db.host=localhost\ndb.port=5432\n"
    result = expand_string(src)
    assert "DB__HOST" in result.values


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB__HOST=localhost\nDB__PORT=5432\nAPP_ENV=prod\n")
    return p


def _run(args, capsys):
    import argparse
    from envdiff.cli_flatten import build_parser, run
    parser = argparse.ArgumentParser()
    build_parser(parser)
    parsed = parser.parse_args(args)
    code = run(parsed)
    captured = capsys.readouterr()
    return code, captured


def test_cli_flatten_stdout_dotenv(env_file, capsys):
    code, captured = _run([str(env_file)], capsys)
    assert code == 0
    assert "db.host=localhost" in captured.out


def test_cli_flatten_json_format(env_file, capsys):
    code, captured = _run([str(env_file), "--format", "json"], capsys)
    assert code == 0
    data = json.loads(captured.out)
    assert "db.host" in data


def test_cli_expand_stdout(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("db.host=localhost\n")
    code, captured = _run([str(p), "--expand"], capsys)
    assert code == 0
    assert "DB__HOST=localhost" in captured.out


def test_cli_missing_file_returns_2(tmp_path, capsys):
    code, captured = _run([str(tmp_path / "missing.env")], capsys)
    assert code == 2


def test_cli_output_to_file(env_file, tmp_path, capsys):
    out = tmp_path / "out.env"
    code, _ = _run([str(env_file), "--output", str(out)], capsys)
    assert code == 0
    assert out.exists()
    assert "db.host" in out.read_text()
