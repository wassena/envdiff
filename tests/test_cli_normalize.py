"""Tests for envdiff.cli_normalize."""
import json
from pathlib import Path

import pytest

from envdiff.cli_normalize import build_parser, run


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("db_host=  localhost  \ndebug=yes\nPORT=5432\n")
    return p


def _run(args: list, parser=None):
    if parser is None:
        parser = build_parser()
    return run(parser.parse_args(args))


def test_stdout_output_dotenv(env_file, capsys):
    code = _run([str(env_file)])
    assert code == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "DEBUG=true" in out


def test_output_to_file(env_file, tmp_path):
    out_file = tmp_path / "out.env"
    code = _run([str(env_file), "-o", str(out_file)])
    assert code == 0
    content = out_file.read_text()
    assert "DB_HOST=localhost" in content


def test_json_format(env_file, capsys):
    code = _run([str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "values" in data
    assert "uppercased" in data
    assert "bool_normalized" in data
    assert data["values"]["DEBUG"] == "true"


def test_no_uppercase_preserves_case(env_file, capsys):
    code = _run([str(env_file), "--no-uppercase"])
    assert code == 0
    out = capsys.readouterr().out
    assert "db_host" in out


def test_missing_file_returns_2(tmp_path):
    code = _run([str(tmp_path / "missing.env")])
    assert code == 2


def test_no_bool_preserves_yes(env_file, capsys):
    code = _run([str(env_file), "--no-bool"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DEBUG=yes" in out
