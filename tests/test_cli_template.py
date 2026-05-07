"""Tests for envdiff.cli_template."""
import json
import os
import textwrap
from pathlib import Path

import pytest

from envdiff.cli_template import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASS=hunter2\nDEBUG=true\n")
    return str(f)


def _run(args_list):
    parser = build_parser()
    args = parser.parse_args(args_list)
    return run(args)


def test_stdout_output_is_redacted(env_file, capsys):
    code = _run([env_file])
    assert code == 0
    out = capsys.readouterr().out
    assert "<REDACTED>" in out
    assert "hunter2" not in out


def test_no_redact_preserves_values(env_file, capsys):
    code = _run([env_file, "--no-redact"])
    assert code == 0
    out = capsys.readouterr().out
    assert "hunter2" in out


def test_keep_preserves_specific_key(env_file, capsys):
    code = _run([env_file, "--keep", "DEBUG"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DEBUG=true" in out
    assert "DB_PASS=<REDACTED>" in out


def test_custom_placeholder(env_file, capsys):
    code = _run([env_file, "--placeholder", "CHANGE_ME"])
    assert code == 0
    out = capsys.readouterr().out
    assert "CHANGE_ME" in out
    assert "<REDACTED>" not in out


def test_output_to_file(env_file, tmp_path):
    out_file = str(tmp_path / ".env.example")
    code = _run([env_file, "--output", out_file])
    assert code == 0
    content = Path(out_file).read_text()
    assert "<REDACTED>" in content


def test_missing_file_returns_2(tmp_path, capsys):
    code = _run([str(tmp_path / "nonexistent.env")])
    assert code == 2
    assert "error" in capsys.readouterr().err.lower()
