"""Tests for envdiff.cli_reconcile."""

import pytest
from pathlib import Path
from envdiff.cli_reconcile import run


BASE_CONTENT = "HOST=localhost\nPORT=5432\nEXTRA=yes\n"
TARGET_CONTENT = "HOST=prod.example.com\nPORT=5432\nSECRET=abc123\n"


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text(BASE_CONTENT)
    target.write_text(TARGET_CONTENT)
    return base, target


def test_dry_run_prints_to_stdout(env_files, capsys):
    base, target = env_files
    rc = run([str(base), str(target), "--dry-run", "--strategy", "fill_missing"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SECRET=abc123" in out


def test_output_to_file(env_files, tmp_path):
    base, target = env_files
    out_file = tmp_path / "reconciled.env"
    rc = run([str(base), str(target), "--output", str(out_file), "--strategy", "full_sync"])
    assert rc == 0
    content = out_file.read_text()
    assert "HOST=prod.example.com" in content
    assert "SECRET=abc123" in content
    assert "EXTRA" not in content


def test_no_differences_returns_zero(tmp_path, capsys):
    same = tmp_path / ".env"
    same.write_text("KEY=value\n")
    rc = run([str(same), str(same)])
    assert rc == 0
    assert "already in sync" in capsys.readouterr().err


def test_placeholder_used_for_new_keys(env_files, capsys):
    base, target = env_files
    rc = run([
        str(base), str(target),
        "--dry-run",
        "--strategy", "fill_missing",
        "--placeholder", "CHANGEME",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SECRET=CHANGEME" in out


def test_stdout_output_when_no_output_flag(env_files, capsys):
    base, target = env_files
    rc = run([str(base), str(target), "--strategy", "overwrite"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "HOST=prod.example.com" in out
