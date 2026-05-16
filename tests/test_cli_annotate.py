"""Tests for envdiff.cli_annotate."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.cli_annotate import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=hunter2\n")
    return p


def _run(argv: list[str]):
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


def test_stdout_output_dotenv(env_file: Path, capsys):
    code = _run([str(env_file), "--set", "DB_HOST=primary host"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost  # primary host" in out


def test_output_to_file(env_file: Path, tmp_path: Path):
    out_file = tmp_path / "out.env"
    code = _run([str(env_file), "--set", "DB_PORT=tcp port", "--output", str(out_file)])
    assert code == 0
    content = out_file.read_text()
    assert "DB_PORT=5432  # tcp port" in content


def test_json_format(env_file: Path, capsys):
    code = _run([str(env_file), "--set", "SECRET=sensitive", "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "SECRET" in data["annotated"]
    assert "  # sensitive" in data["values"]["SECRET"]


def test_overwrite_replaces_comment(tmp_path: Path, capsys):
    p = tmp_path / ".env"
    p.write_text("KEY=value  # old\n")
    code = _run([str(p), "--set", "KEY=new comment", "--overwrite"])
    assert code == 0
    out = capsys.readouterr().out
    assert "# new comment" in out
    assert "# old" not in out


def test_missing_file_returns_2(tmp_path: Path):
    code = _run([str(tmp_path / "ghost.env"), "--set", "K=v"])
    assert code == 2


def test_invalid_pair_returns_2(env_file: Path):
    code = _run([str(env_file), "--set", "NOEQUALSSIGN"])
    assert code == 2
