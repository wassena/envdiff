"""Tests for envdiff.cli_snapshot sub-commands."""

import json
import pytest

from envdiff.cli_snapshot import run


@pytest.fixture()
def env_files(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("HOST=localhost\nPORT=5432\nONLY_A=yes\n")
    b.write_text("HOST=remotehost\nPORT=5432\nONLY_B=yes\n")
    return tmp_path, str(a), str(b)


def test_capture_creates_json_file(env_files, capsys):
    tmp_path, a, _ = env_files
    out = str(tmp_path / "snap.json")
    code = run(["capture", a, out])
    assert code == 0
    with open(out) as fh:
        data = json.load(fh)
    assert data["values"]["HOST"] == "localhost"
    captured = capsys.readouterr()
    assert "snap.json" in captured.out


def test_capture_with_label(env_files):
    tmp_path, a, _ = env_files
    out = str(tmp_path / "snap.json")
    run(["capture", a, out, "--label", "staging"])
    with open(out) as fh:
        data = json.load(fh)
    assert data["label"] == "staging"


def test_capture_missing_env_returns_2(tmp_path):
    code = run(["capture", str(tmp_path / "nope.env"), str(tmp_path / "out.json")])
    assert code == 2


def test_compare_two_env_files_text(env_files, capsys):
    _, a, b = env_files
    code = run(["compare", a, b])
    assert code == 0
    out = capsys.readouterr().out
    assert "HOST" in out


def test_compare_exit_code_on_diff(env_files):
    _, a, b = env_files
    code = run(["compare", a, b, "--exit-code"])
    assert code == 1


def test_compare_no_diff_exit_code_zero(tmp_path):
    same = tmp_path / "same.env"
    same.write_text("KEY=value\n")
    code = run(["compare", str(same), str(same), "--exit-code"])
    assert code == 0


def test_compare_snapshot_vs_env(env_files):
    tmp_path, a, b = env_files
    snap = str(tmp_path / "snap_a.json")
    run(["capture", a, snap])
    code = run(["compare", snap, b, "--exit-code"])
    assert code == 1


def test_compare_json_format(env_files, capsys):
    _, a, b = env_files
    run(["compare", a, b, "--format", "json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert "changed" in parsed or "missing_in_b" in parsed or "missing_in_a" in parsed
