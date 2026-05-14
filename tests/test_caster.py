"""Tests for envdiff.caster and envdiff.cli_cast."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from envdiff.caster import (
    CastResult,
    _infer,
    cast_count,
    cast_string,
    cast_values,
    summary,
)


# ---------------------------------------------------------------------------
# _infer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("true", (True, "bool")),
    ("True", (True, "bool")),
    ("yes", (True, "bool")),
    ("1", (True, "bool")),  # '1' maps to bool True
    ("false", (False, "bool")),
    ("no", (False, "bool")),
    ("0", (False, "bool")),
    ("42", (42, "int")),
    ("-7", (-7, "int")),
    ("3.14", (3.14, "float")),
    ("hello", ("hello", "str")),
    ("", ("", "str")),
])
def test_infer(raw, expected):
    assert _infer(raw) == expected


# ---------------------------------------------------------------------------
# cast_values / cast_string
# ---------------------------------------------------------------------------

SAMPLE = textwrap.dedent("""\
    DEBUG=true
    PORT=8080
    RATIO=0.5
    NAME=myapp
    ENABLED=false
""")


@pytest.fixture()
def result() -> CastResult:
    return cast_string(SAMPLE, source="test")


def test_cast_string_bool_true(result):
    assert result.values["DEBUG"] is True
    assert result.casts["DEBUG"] == "bool"


def test_cast_string_bool_false(result):
    assert result.values["ENABLED"] is False
    assert result.casts["ENABLED"] == "bool"


def test_cast_string_int(result):
    assert result.values["PORT"] == 8080
    assert result.casts["PORT"] == "int"


def test_cast_string_float(result):
    assert result.values["RATIO"] == pytest.approx(0.5)
    assert result.casts["RATIO"] == "float"


def test_cast_string_str(result):
    assert result.values["NAME"] == "myapp"
    assert result.casts["NAME"] == "str"


def test_cast_count(result):
    # DEBUG, PORT, RATIO, ENABLED are non-str  → 4
    assert cast_count(result) == 4


def test_summary_excludes_str(result):
    lines = summary(result)
    keys_in_summary = [line.split(":")[0] for line in lines]
    assert "NAME" not in keys_in_summary
    assert "PORT" in keys_in_summary


def test_cast_values_empty():
    r = cast_values({})
    assert r.values == {}
    assert cast_count(r) == 0


# ---------------------------------------------------------------------------
# cli_cast
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(SAMPLE)
    return p


def _run(args, capsys):
    import argparse
    from envdiff.cli_cast import build_parser, run
    parser = build_parser()
    parsed = parser.parse_args(args)
    code = run(parsed)
    out = capsys.readouterr().out
    return code, out


def test_cli_text_output_contains_key(env_file, capsys):
    code, out = _run([str(env_file)], capsys)
    assert code == 0
    assert "PORT" in out


def test_cli_non_string_only_hides_str(env_file, capsys):
    code, out = _run([str(env_file), "--non-string-only"], capsys)
    assert code == 0
    assert "NAME" not in out
    assert "PORT" in out


def test_cli_json_format(env_file, capsys):
    code, out = _run([str(env_file), "--format", "json"], capsys)
    assert code == 0
    data = json.loads(out)
    assert "cast_count" in data
    assert data["cast_count"] == 4


def test_cli_missing_file_returns_2(tmp_path, capsys):
    code, _ = _run([str(tmp_path / "missing.env")], capsys)
    assert code == 2
