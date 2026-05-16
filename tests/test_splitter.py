"""Tests for envdiff.splitter and cli_split."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.splitter import split_string, split_by_prefix, write_split, to_env_string, SplitResult
from envdiff.cli_split import run, build_parser


SAMPLE = """
DB_HOST=localhost
DB_PORT=5432
AWS_KEY=abc
AWS_SECRET=xyz
APP_DEBUG=true
APP_ENV=production
PLAIN=value
""".strip()


# ---------------------------------------------------------------------------
# splitter unit tests
# ---------------------------------------------------------------------------

def test_split_string_creates_prefix_buckets():
    result = split_string(SAMPLE)
    assert "DB" in result.files
    assert "AWS" in result.files
    assert "APP" in result.files


def test_split_string_correct_members():
    result = split_string(SAMPLE)
    assert result.files["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result.files["AWS"] == {"AWS_KEY": "abc", "AWS_SECRET": "xyz"}


def test_ungrouped_key_captured():
    result = split_string(SAMPLE)
    assert "PLAIN" in result.ungrouped


def test_no_ungrouped_flag_drops_plain_keys():
    result = split_string(SAMPLE, include_ungrouped=False)
    assert result.ungrouped == {}


def test_file_count():
    result = split_string(SAMPLE)
    assert result.file_count == 3  # DB, AWS, APP


def test_total_keys():
    result = split_string(SAMPLE)
    assert result.total_keys == 7


def test_to_env_string_format():
    env = {"A": "1", "B": "2"}
    out = to_env_string(env)
    assert "A=1" in out
    assert "B=2" in out


def test_write_split_creates_files(tmp_path):
    result = split_string(SAMPLE)
    written = write_split(result, tmp_path)
    names = {p.name for p in written}
    assert "db.env" in names
    assert "aws.env" in names
    assert "ungrouped.env" in names


def test_write_split_file_contents(tmp_path):
    result = split_string(SAMPLE)
    write_split(result, tmp_path)
    content = (tmp_path / "db.env").read_text()
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.env"
    p.write_text(SAMPLE)
    return p


def _run(args: list[str]) -> tuple[int, str]:
    import io, contextlib
    parser = build_parser()
    ns = parser.parse_args(args)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run(ns)
    return code, buf.getvalue()


def test_stdout_text_contains_headers(env_file):
    code, out = _run([str(env_file)])
    assert code == 0
    assert "# --- DB ---" in out


def test_stdout_json_format(env_file):
    code, out = _run([str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert "DB" in data
    assert data["DB"]["DB_HOST"] == "localhost"


def test_output_dir_writes_files(env_file, tmp_path):
    out_dir = tmp_path / "split_out"
    code, _ = _run([str(env_file), "--output-dir", str(out_dir)])
    assert code == 0
    assert (out_dir / "db.env").exists()


def test_missing_file_returns_2(tmp_path):
    parser = build_parser()
    ns = parser.parse_args([str(tmp_path / "nope.env")])
    assert run(ns) == 2
