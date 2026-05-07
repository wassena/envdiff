"""Tests for envdiff.linter."""
import pytest
from envdiff.linter import lint_lines, lint_file, LintIssue


def lines(*args: str):
    return list(args)


# --- E001 malformed ---

def test_malformed_line_flagged():
    result = lint_lines(lines('BADLINE'))
    assert not result.ok
    issues = result.by_code('E001')
    assert len(issues) == 1
    assert issues[0].line == 1


def test_comment_and_blank_ignored():
    result = lint_lines(lines('', '# comment', 'KEY=value'))
    assert result.ok


# --- E002 duplicate ---

def test_duplicate_key_flagged():
    result = lint_lines(lines('KEY=a', 'KEY=b'))
    issues = result.by_code('E002')
    assert len(issues) == 1
    assert issues[0].line == 2
    assert 'first seen on line 1' in issues[0].message


def test_no_duplicate_no_flag():
    result = lint_lines(lines('KEY_A=1', 'KEY_B=2'))
    assert result.by_code('E002') == []


# --- W001 naming ---

def test_lowercase_key_warns():
    result = lint_lines(lines('mykey=value'))
    issues = result.by_code('W001')
    assert len(issues) == 1


def test_key_starting_with_digit_warns():
    result = lint_lines(lines('1KEY=value'))
    assert result.by_code('W001')


def test_valid_upper_snake_no_warn():
    result = lint_lines(lines('MY_KEY=value', 'KEY2=val'))
    assert result.by_code('W001') == []


# --- W002 sensitive empty ---

def test_sensitive_empty_value_warns():
    result = lint_lines(lines('API_KEY=', 'DB_PASSWORD='))
    issues = result.by_code('W002')
    assert len(issues) == 2


def test_sensitive_nonempty_no_warn():
    result = lint_lines(lines('API_KEY=abc123'))
    assert result.by_code('W002') == []


# --- W003 unquoted whitespace ---

def test_unquoted_space_warns():
    result = lint_lines(lines('GREETING=hello world'))
    issues = result.by_code('W003')
    assert len(issues) == 1


def test_quoted_space_no_warn():
    result = lint_lines(lines('GREETING="hello world"'))
    assert result.by_code('W003') == []


# --- lint_file ---

def test_lint_file_ok(tmp_path):
    f = tmp_path / '.env'
    f.write_text('KEY=value\nOTHER=123\n')
    result = lint_file(str(f))
    assert result.ok


def test_lint_file_missing_raises():
    with pytest.raises(FileNotFoundError):
        lint_file('/nonexistent/.env')


# --- str representation ---

def test_issue_str():
    issue = LintIssue(line=3, key='FOO', code='W001', message='bad name')
    assert 'Line 3' in str(issue)
    assert 'W001' in str(issue)
    assert 'FOO' in str(issue)
