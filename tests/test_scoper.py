"""Tests for envdiff.scoper and envdiff.cli_scope."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envdiff.scoper import (
    ScopeResult,
    dropped_count,
    kept_count,
    scope_keys,
    scope_string,
    to_env_string,
)
from envdiff.cli_scope import build_parser, run


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_scope_keys_keeps_matching_prefix():
    result = scope_keys(SAMPLE, "DB")
    assert set(result.kept.keys()) == {"HOST", "PORT"}


def test_scope_keys_drops_non_matching():
    result = scope_keys(SAMPLE, "DB")
    assert "APP_NAME" in result.dropped
    assert "SECRET_KEY" in result.dropped


def test_scope_keys_no_strip_preserves_prefix():
    result = scope_keys(SAMPLE, "DB", strip_prefix=False)
    assert "DB_HOST" in result.kept
    assert "DB_PORT" in result.kept


def test_scope_keys_invert_returns_non_matching():
    result = scope_keys(SAMPLE, "DB", invert=True)
    assert "APP_NAME" in result.kept
    assert "SECRET_KEY" in result.kept
    assert "HOST" not in result.kept


def test_kept_count_and_dropped_count():
    result = scope_keys(SAMPLE, "APP")
    assert kept_count(result) == 2
    assert dropped_count(result) == 3


def test_to_env_string_format():
    result = scope_keys(SAMPLE, "DB")
    text = to_env_string(result)
    assert "HOST=localhost" in text
    assert "PORT=5432" in text
    assert "APP_NAME" not in text


def test_scope_string_parses_and_scopes():
    source = "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n"
    result = scope_string(source, "DB")
    assert result.kept == {"HOST": "localhost", "PORT": "5432"}


def test_scope_string_custom_separator():
    source = "DB.HOST=localhost\nDB.PORT=5432\nAPP.NAME=myapp\n"
    result = scope_string(source, "DB", separator=".")
    assert "HOST" in result.kept


def test_empty_scope_returns_empty_kept():
    result = scope_keys(SAMPLE, "NONEXISTENT")
    assert result.kept == {}
    assert len(result.dropped) == len(SAMPLE)


# --- CLI tests ---

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n")
    return p


def _run(args: list[str]) -> tuple[int, str]:
    parser = build_parser()
    ns = parser.parse_args(args)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run(ns)
    return code, buf.getvalue()


def test_cli_stdout_dotenv(env_file: Path):
    code, out = _run([str(env_file), "DB"])
    assert code == 0
    assert "HOST=localhost" in out
    assert "APP_NAME" not in out


def test_cli_json_format(env_file: Path):
    code, out = _run([str(env_file), "DB", "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert data["scope"] == "DB"
    assert "HOST" in data["kept"]


def test_cli_missing_file_returns_2(tmp_path: Path):
    parser = build_parser()
    ns = parser.parse_args([str(tmp_path / "missing.env"), "DB"])
    assert run(ns) == 2


def test_cli_output_to_file(env_file: Path, tmp_path: Path):
    out_file = tmp_path / "out.env"
    parser = build_parser()
    ns = parser.parse_args([str(env_file), "DB", "-o", str(out_file)])
    code = run(ns)
    assert code == 0
    assert "HOST=localhost" in out_file.read_text()
