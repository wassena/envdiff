"""Integration tests for the redact CLI sub-command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.cli_redact import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=s3cr3t\n"
        "API_KEY=abc123\n"
        "DEBUG=true\n",
        encoding="utf-8",
    )
    return p


def _run(argv: list[str]) -> tuple[int, str]:
    import io, contextlib

    parser = build_parser()
    args = parser.parse_args(argv)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run(args)
    return code, buf.getvalue()


def test_stdout_output_redacts_all(env_file: Path):
    code, out = _run([str(env_file)])
    assert code == 0
    assert "s3cr3t" not in out
    assert "abc123" not in out
    assert "myapp" not in out


def test_specific_keys_only_redacted(env_file: Path):
    code, out = _run([str(env_file), "--keys", "DB_PASSWORD"])
    assert code == 0
    assert "myapp" in out
    assert "true" in out
    assert "s3cr3t" not in out


def test_json_format(env_file: Path):
    code, out = _run([str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert "APP_NAME" in data
    assert data["DB_PASSWORD"] == "********"


def test_custom_char_and_length(env_file: Path):
    code, out = _run([str(env_file), "--keys", "DB_PASSWORD", "--char", "#", "--length", "4"])
    assert code == 0
    assert "####" in out


def test_output_to_file(env_file: Path, tmp_path: Path):
    out_file = tmp_path / "redacted.env"
    parser = build_parser()
    args = parser.parse_args([str(env_file), "--output", str(out_file)])
    code = run(args)
    assert code == 0
    content = out_file.read_text(encoding="utf-8")
    assert "s3cr3t" not in content


def test_missing_file_returns_2(tmp_path: Path):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "nonexistent.env")])
    code = run(args)
    assert code == 2
