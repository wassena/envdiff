"""Tests for envdiff.cli_diff."""

import json
import os
import textwrap
from pathlib import Path

import pytest

from envdiff.cli_diff import run


@pytest.fixture()
def env_files(tmp_path: Path):
    """Return paths to two temporary .env files."""
    file_a = tmp_path / ".env.example"
    file_b = tmp_path / ".env"
    file_a.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DEBUG=false
            SECRET_KEY=changeme
            """
        )
    )
    file_b.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DEBUG=true
            EXTRA_KEY=surprise
            """
        )
    )
    return str(file_a), str(file_b)


def test_no_differences_returns_zero(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text("KEY=val\n")
    assert run([str(f), str(f)]) == 0


def test_exit_code_flag_returns_one_on_diff(env_files, capsys):
    file_a, file_b = env_files
    code = run([file_a, file_b, "--exit-code"])
    assert code == 1


def test_exit_code_flag_absent_returns_zero_despite_diff(env_files):
    file_a, file_b = env_files
    code = run([file_a, file_b])
    assert code == 0


def test_text_output_contains_keys(env_files, capsys):
    file_a, file_b = env_files
    run([file_a, file_b])
    captured = capsys.readouterr()
    assert "SECRET_KEY" in captured.out
    assert "EXTRA_KEY" in captured.out
    assert "DEBUG" in captured.out


def test_json_format_is_valid_json(env_files, capsys):
    file_a, file_b = env_files
    run([file_a, file_b, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_b" in data
    assert "missing_in_a" in data
    assert "changed" in data


def test_output_to_file(env_files, tmp_path: Path):
    file_a, file_b = env_files
    out_file = tmp_path / "diff.txt"
    run([file_a, file_b, "--output", str(out_file)])
    assert out_file.exists()
    content = out_file.read_text()
    assert "SECRET_KEY" in content


def test_missing_file_returns_two(tmp_path: Path):
    missing = str(tmp_path / "ghost.env")
    existing = tmp_path / ".env"
    existing.write_text("K=v\n")
    code = run([missing, str(existing)])
    assert code == 2
