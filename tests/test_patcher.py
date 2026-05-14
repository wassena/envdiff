"""Tests for envdiff.patcher and envdiff.cli_patch."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.patcher import (
    PatchResult,
    added_count,
    patch_string,
    patch_values,
    to_env_string,
    updated_count,
)


BASE_ENV = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


# ---------------------------------------------------------------------------
# patch_values
# ---------------------------------------------------------------------------

def test_patch_values_updates_existing_key():
    result = patch_values(BASE_ENV, {"PORT": "9999"})
    assert result.env["PORT"] == "9999"
    assert "PORT" in result.updated


def test_patch_values_adds_new_key_by_default():
    result = patch_values(BASE_ENV, {"NEW_KEY": "hello"})
    assert result.env["NEW_KEY"] == "hello"
    assert "NEW_KEY" in result.added


def test_patch_values_no_add_ignores_new_key():
    result = patch_values(BASE_ENV, {"NEW_KEY": "hello"}, add_new=False)
    assert "NEW_KEY" not in result.env
    assert added_count(result) == 0


def test_patch_values_unchanged_when_same_value():
    result = patch_values(BASE_ENV, {"HOST": "localhost"})
    assert "HOST" in result.unchanged
    assert "HOST" not in result.updated


def test_patch_values_multiple_patches():
    result = patch_values(BASE_ENV, {"PORT": "6543", "DEBUG": "true", "EXTRA": "x"})
    assert updated_count(result) == 2
    assert added_count(result) == 1


def test_patch_values_preserves_unpatched_keys():
    result = patch_values(BASE_ENV, {"PORT": "1111"})
    assert result.env["HOST"] == "localhost"
    assert result.env["DEBUG"] == "false"


# ---------------------------------------------------------------------------
# patch_string
# ---------------------------------------------------------------------------

def test_patch_string_parses_and_patches():
    source = "HOST=localhost\nPORT=5432\n"
    result = patch_string(source, {"PORT": "9000"})
    assert result.env["PORT"] == "9000"
    assert "PORT" in result.updated


def test_patch_string_adds_new_key():
    source = "HOST=localhost\n"
    result = patch_string(source, {"TOKEN": "abc123"})
    assert result.env["TOKEN"] == "abc123"
    assert "TOKEN" in result.added


# ---------------------------------------------------------------------------
# to_env_string
# ---------------------------------------------------------------------------

def test_to_env_string_produces_dotenv_lines():
    result = patch_values({"A": "1", "B": "2"}, {})
    output = to_env_string(result)
    assert "A=1" in output
    assert "B=2" in output


def test_to_env_string_empty_env_returns_empty_string():
    result = PatchResult(env={})
    assert to_env_string(result) == ""


# ---------------------------------------------------------------------------
# cli_patch via subprocess-style invocation
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=5432\nDEBUG=false\n")
    return p


def _run(argv):
    from envdiff.cli_patch import run
    return run(argv)


def test_cli_patch_stdout(env_file, capsys):
    code = _run([str(env_file), "PORT=9999"])
    assert code == 0
    out = capsys.readouterr().out
    assert "PORT=9999" in out


def test_cli_patch_output_to_file(env_file, tmp_path):
    out_file = tmp_path / "out.env"
    code = _run([str(env_file), "DEBUG=true", "-o", str(out_file)])
    assert code == 0
    content = out_file.read_text()
    assert "DEBUG=true" in content


def test_cli_patch_json_format(env_file, capsys):
    code = _run([str(env_file), "PORT=1111", "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["PORT"] == "1111"


def test_cli_patch_missing_file_returns_2(tmp_path):
    code = _run([str(tmp_path / "missing.env"), "K=V"])
    assert code == 2


def test_cli_patch_invalid_patch_exits(env_file):
    with pytest.raises(SystemExit) as exc_info:
        _run([str(env_file), "NOEQUALSSIGN"])
    assert exc_info.value.code == 2
