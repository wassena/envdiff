"""Integration tests for the `envdiff group` CLI sub-command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.cli_group import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    content = (
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "AWS_KEY=abc\n"
        "AWS_SECRET=xyz\n"
        "PORT=8080\n"
    )
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def _run(argv: list[str]) -> tuple[int, str]:
    import io
    import contextlib

    parser = pytest.importorskip("argparse").ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_parser(subs)
    args = parser.parse_args(["group"] + argv)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run(args)
    return code, buf.getvalue()


def test_text_output_contains_section_headers(env_file: Path):
    code, out = _run([str(env_file)])
    assert code == 0
    assert "# [DB]" in out
    assert "# [AWS]" in out


def test_text_output_contains_ungrouped(env_file: Path):
    code, out = _run([str(env_file)])
    assert "# [ungrouped]" in out
    assert "PORT=8080" in out


def test_json_format_returns_groups(env_file: Path):
    code, out = _run([str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert "DB" in data["groups"]
    assert "AWS" in data["groups"]


def test_json_format_total_keys(env_file: Path):
    code, out = _run([str(env_file), "--format", "json"])
    data = json.loads(out)
    assert data["total_keys"] == 5


def test_min_group_size_filters_small_groups(env_file: Path):
    code, out = _run([str(env_file), "--min-group-size", "2"])
    assert code == 0
    assert "# [DB]" in out
    assert "# [AWS]" in out


def test_missing_file_returns_exit_code_2(tmp_path: Path):
    code, _ = _run([str(tmp_path / "missing.env")])
    assert code == 2
