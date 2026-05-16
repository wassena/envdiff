"""Tests for envdiff.cli_strip."""
import json
from pathlib import Path

import pytest

from envdiff.cli_strip import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc\nAPP_NAME=myapp\n")
    return p


def _run(args: list, tmp_path: Path | None = None):
    parser = build_parser()
    ns = parser.parse_args(args)
    return run(ns)


def test_stdout_removes_key(env_file, capsys):
    code = _run([str(env_file), "-k", "DB_PORT"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_PORT" not in out
    assert "DB_HOST=localhost" in out


def test_pattern_removes_matching(env_file, capsys):
    code = _run([str(env_file), "-p", r"^DB_"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_HOST" not in out
    assert "SECRET_KEY=abc" in out


def test_output_to_file(env_file, tmp_path):
    out_file = tmp_path / "out.env"
    code = _run([str(env_file), "-k", "SECRET_KEY", "-o", str(out_file)])
    assert code == 0
    content = out_file.read_text()
    assert "SECRET_KEY" not in content
    assert "DB_HOST" in content


def test_json_format(env_file, capsys):
    code = _run([str(env_file), "-k", "APP_NAME", "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "APP_NAME" not in data["values"]
    assert "APP_NAME" in data["stripped"]


def test_missing_file_returns_2(tmp_path):
    code = _run([str(tmp_path / "missing.env")])
    assert code == 2


def test_no_criteria_keeps_all(env_file, capsys):
    code = _run([str(env_file)])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "APP_NAME=myapp" in out
