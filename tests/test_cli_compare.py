"""Tests for envdiff.cli_compare."""
import json
import sys
from pathlib import Path

import pytest

from envdiff.cli_compare import build_parser, run

ENV_A = "HOST=localhost\nPORT=5432\nDEBUG=true\n"
ENV_B = "HOST=localhost\nPORT=5433\nNEW_KEY=hello\n"


@pytest.fixture
def env_files(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(ENV_A)
    b.write_text(ENV_B)
    return str(a), str(b)


def _run(argv, capsys=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    code = run(args)
    return code


def test_text_output_contains_sections(env_files, capsys):
    a, b = env_files
    parser = build_parser()
    args = parser.parse_args([a, b])
    run(args)
    out = capsys.readouterr().out
    assert "Only in A" in out
    assert "Only in B" in out
    assert "Changed" in out


def test_json_format_keys(env_files, capsys):
    a, b = env_files
    parser = build_parser()
    args = parser.parse_args([a, b, "--format", "json"])
    run(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "only_in_a" in data
    assert "only_in_b" in data
    assert "changed" in data
    assert "similarity" in data


def test_exit_code_flag_returns_one_on_diff(env_files):
    a, b = env_files
    parser = build_parser()
    args = parser.parse_args([a, b, "--exit-code"])
    assert run(args) == 1


def test_no_diff_returns_zero(tmp_path, capsys):
    env = "A=1\nB=2\n"
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(env)
    b.write_text(env)
    parser = build_parser()
    args = parser.parse_args([str(a), str(b), "--exit-code"])
    assert run(args) == 0


def test_score_flag_prints_float(env_files, capsys):
    a, b = env_files
    parser = build_parser()
    args = parser.parse_args([a, b, "--score"])
    code = run(args)
    out = capsys.readouterr().out.strip()
    assert code == 0
    float(out)  # should not raise


def test_missing_file_returns_two(tmp_path):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "nope.env"), str(tmp_path / "also.env")])
    assert run(args) == 2
