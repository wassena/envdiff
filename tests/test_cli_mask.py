"""Tests for envdiff.cli_mask."""
import json
import sys
from pathlib import Path

import pytest

from envdiff.cli_mask import run
from envdiff.masker import DEFAULT_MASK


@pytest.fixture()
def env_files(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("APP_NAME=myapp\nDB_PASSWORD=secret\nAPI_KEY=key123\nPORT=5000\n")
    return {"env": env, "tmp": tmp_path}


def _run(args, monkeypatch):
    import argparse
    import envdiff.cli_mask as mod

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    mod.build_parser(sub)
    parsed = parser.parse_args(["mask"] + args)
    return mod.run(parsed)


def test_stdout_output_dotenv(env_files, monkeypatch, capsys):
    code = _run([str(env_files["env"])], monkeypatch)
    assert code == 0
    out = capsys.readouterr().out
    assert f"DB_PASSWORD={DEFAULT_MASK}" in out
    assert "APP_NAME=myapp" in out


def test_output_to_file(env_files, monkeypatch):
    out_file = env_files["tmp"] / "masked.env"
    code = _run([str(env_files["env"]), "--output", str(out_file)], monkeypatch)
    assert code == 0
    content = out_file.read_text()
    assert f"DB_PASSWORD={DEFAULT_MASK}" in content


def test_json_format(env_files, monkeypatch, capsys):
    code = _run([str(env_files["env"]), "--format", "json"], monkeypatch)
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["DB_PASSWORD"] == DEFAULT_MASK
    assert data["APP_NAME"] == "myapp"


def test_custom_mask_string(env_files, monkeypatch, capsys):
    code = _run([str(env_files["env"]), "--mask", "HIDDEN"], monkeypatch)
    assert code == 0
    assert "DB_PASSWORD=HIDDEN" in capsys.readouterr().out


def test_list_masked_writes_to_stderr(env_files, monkeypatch, capsys):
    code = _run([str(env_files["env"]), "--list-masked"], monkeypatch)
    assert code == 0
    err = capsys.readouterr().err
    assert "masked: DB_PASSWORD" in err
    assert "masked: API_KEY" in err


def test_missing_file_returns_2(tmp_path, monkeypatch):
    code = _run([str(tmp_path / "nonexistent.env")], monkeypatch)
    assert code == 2
