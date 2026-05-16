"""Tests for envdiff.freezer and envdiff.cli_freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.freezer import (
    FreezeResult,
    freeze_string,
    freeze_values,
    frozen_count,
    to_env_string,
)


ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


# ---------------------------------------------------------------------------
# freeze_values
# ---------------------------------------------------------------------------

def test_freeze_all_keys_by_default():
    result = freeze_values(ENV)
    assert set(result.frozen_keys) == {"DB_HOST", "DB_PORT", "SECRET"}
    assert result.already_frozen == []


def test_freeze_specific_keys_only():
    result = freeze_values(ENV, keys=["SECRET"])
    assert result.frozen_keys == ["SECRET"]
    assert "DB_HOST" not in result.frozen_keys


def test_frozen_count_matches_list():
    result = freeze_values(ENV, keys=["DB_HOST", "DB_PORT"])
    assert frozen_count(result) == 2


def test_already_frozen_detected():
    already = "DB_HOST=localhost  # frozen\nDB_PORT=5432\n"
    result = freeze_values(already)
    assert "DB_HOST" in result.already_frozen
    assert "DB_HOST" not in result.frozen_keys
    assert "DB_PORT" in result.frozen_keys


def test_values_dict_populated():
    result = freeze_values(ENV)
    assert result.values["DB_HOST"] == "localhost"
    assert result.values["SECRET"] == "abc123"


def test_missing_key_ignored_gracefully():
    result = freeze_values(ENV, keys=["NONEXISTENT"])
    assert result.frozen_keys == []
    assert result.already_frozen == []


# ---------------------------------------------------------------------------
# freeze_string
# ---------------------------------------------------------------------------

def test_freeze_string_appends_marker():
    out = freeze_string("FOO=bar\n")
    assert "# frozen" in out
    assert "FOO=bar" in out


def test_freeze_string_specific_key_only():
    out = freeze_string("FOO=bar\nBAZ=qux\n", keys=["FOO"])
    lines = {l.split("=")[0].strip(): l for l in out.splitlines() if "=" in l}
    assert "# frozen" in lines["FOO"]
    assert "# frozen" not in lines["BAZ"]


def test_freeze_string_does_not_double_mark():
    already = "FOO=bar  # frozen"
    out = freeze_string(already)
    assert out.count("# frozen") == 1


def test_freeze_string_preserves_comments_and_blanks():
    src = "# header\n\nFOO=1\n"
    out = freeze_string(src)
    assert "# header" in out
    assert out.count("\n") >= 2


# ---------------------------------------------------------------------------
# to_env_string
# ---------------------------------------------------------------------------

def test_to_env_string_round_trips_values():
    result = freeze_values("A=1\nB=2\n")
    s = to_env_string(result)
    assert "A=1" in s
    assert "B=2" in s


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(ENV)
    return p


def _run(args: list[str]) -> tuple[int, str]:
    import io
    from contextlib import redirect_stdout
    from envdiff.cli_freeze import build_parser, run as cli_run
    parser = build_parser()
    namespace = parser.parse_args(args)
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli_run(namespace)
    return code, buf.getvalue()


def test_cli_stdout_contains_frozen_marker(env_file: Path):
    code, out = _run([str(env_file)])
    assert code == 0
    assert "# frozen" in out


def test_cli_output_to_file(env_file: Path, tmp_path: Path):
    out_file = tmp_path / "out.env"
    code, _ = _run([str(env_file), "-o", str(out_file)])
    assert code == 0
    assert "# frozen" in out_file.read_text()


def test_cli_json_format(env_file: Path):
    code, out = _run([str(env_file), "--format", "json"])
    assert code == 0
    data = json.loads(out)
    assert "frozen" in data
    assert "values" in data


def test_cli_missing_file_returns_2(tmp_path: Path):
    code, _ = _run([str(tmp_path / "ghost.env")])
    assert code == 2
