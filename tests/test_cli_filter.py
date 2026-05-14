"""Tests for envdiff.cli_filter."""

import json
import os
from pathlib import Path

import pytest

from envdiff.cli_filter import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PASS=secret\nAPP_ENV=prod\nTEST_FLAG=1\n")
    return str(p)


def _run(args_list):
    parser = build_parser()
    args = parser.parse_args(args_list)
    return run(args)


def test_stdout_removes_key(env_file, capsys):
    code = _run([env_file, "--keys", "DB_PASS"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_PASS" not in out
    assert "DB_HOST" in out


def test_stdout_pattern_removes_matching(env_file, capsys):
    code = _run([env_file, "--pattern", "^DB_"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_HOST" not in out
    assert "APP_ENV" in out


def test_invert_keeps_only_matched(env_file, capsys):
    code = _run([env_file, "--keys", "APP_ENV", "--invert"])
    assert code == 0
    out = capsys.readouterr().out
    assert "APP_ENV=prod" in out
    assert "DB_HOST" not in out


def test_json_format(env_file, capsys):
    code = _run([env_file, "--keys", "DB_PASS", "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "kept" in data and "removed" in data
    assert "DB_PASS" in data["removed"]


def test_output_to_file(env_file, tmp_path):
    out_path = str(tmp_path / "out.env")
    code = _run([env_file, "--keys", "TEST_FLAG", "-o", out_path])
    assert code == 0
    content = Path(out_path).read_text()
    assert "TEST_FLAG" not in content
    assert "DB_HOST" in content


def test_missing_file_returns_2(tmp_path):
    code = _run([str(tmp_path / "nonexistent.env")])
    assert code == 2
