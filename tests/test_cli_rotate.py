"""Tests for envdiff.cli_rotate."""
import json
from pathlib import Path

import pytest

from envdiff.cli_rotate import build_parser, run


@pytest.fixture()
def env_files(tmp_path: Path):
    src = tmp_path / ".env"
    src.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    return {"src": src, "tmp": tmp_path}


def _run(args_list):
    parser = build_parser()
    args = parser.parse_args(args_list)
    return run(args)


def test_stdout_output_dotenv(env_files, capsys):
    rc = _run([str(env_files["src"]), "--map", "DB_HOST=DATABASE_HOST"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DATABASE_HOST=localhost" in out
    assert "DB_HOST" not in out


def test_output_to_file(env_files):
    out_file = env_files["tmp"] / "out.env"
    rc = _run([str(env_files["src"]), "--map", "DB_HOST=DATABASE_HOST", "-o", str(out_file)])
    assert rc == 0
    content = out_file.read_text()
    assert "DATABASE_HOST=localhost" in content


def test_json_format(env_files, capsys):
    rc = _run([str(env_files["src"]), "--map", "DB_HOST=DATABASE_HOST", "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "DATABASE_HOST" in data["values"]
    assert "DB_HOST" in data["rotated"]


def test_keep_old_flag(env_files, capsys):
    rc = _run([str(env_files["src"]), "--map", "DB_HOST=DATABASE_HOST", "--keep-old"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DATABASE_HOST=localhost" in out
    assert "DB_HOST=localhost" in out


def test_map_file(env_files, capsys):
    map_file = env_files["tmp"] / "map.json"
    map_file.write_text(json.dumps({"DB_PORT": "DATABASE_PORT"}))
    rc = _run([str(env_files["src"]), "--map-file", str(map_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DATABASE_PORT=5432" in out


def test_no_map_returns_error(env_files, capsys):
    rc = _run([str(env_files["src"])])
    assert rc == 2
