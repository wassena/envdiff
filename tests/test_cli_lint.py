"""Tests for envdiff.cli_lint."""
import json
import pytest
from envdiff.cli_lint import build_parser, run


@pytest.fixture()
def env_files(tmp_path):
    clean = tmp_path / 'clean.env'
    clean.write_text('KEY=value\nOTHER=123\n')

    dirty = tmp_path / 'dirty.env'
    dirty.write_text('key=lowercase\nAPI_SECRET=\nKEY=dup\nKEY=dup\nBAD LINE\n')

    return {'clean': str(clean), 'dirty': str(dirty)}


def _run(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


def test_clean_file_returns_zero(env_files):
    code = _run([env_files['clean']])
    assert code == 0


def test_dirty_file_returns_one(env_files):
    code = _run([env_files['dirty']])
    assert code == 1


def test_text_output_ok(env_files, capsys):
    _run([env_files['clean']])
    out = capsys.readouterr().out
    assert 'OK' in out


def test_text_output_shows_issues(env_files, capsys):
    _run([env_files['dirty']])
    out = capsys.readouterr().out
    assert 'E002' in out or 'W001' in out


def test_json_output_parseable(env_files, capsys):
    _run([env_files['dirty'], '--format', 'json'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert env_files['dirty'] in data
    assert isinstance(data[env_files['dirty']], list)


def test_json_output_clean_file_empty_list(env_files, capsys):
    _run([env_files['clean'], '--format', 'json'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[env_files['clean']] == []


def test_strict_mode_warnings_become_error(env_files):
    # dirty.env has warnings; strict should still return 1
    code = _run([env_files['dirty'], '--strict'])
    assert code == 1


def test_missing_file_returns_two(tmp_path):
    code = _run([str(tmp_path / 'missing.env')])
    assert code == 2


def test_multiple_files_reported(env_files, capsys):
    _run([env_files['clean'], env_files['dirty'], '--format', 'json'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
