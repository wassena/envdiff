"""Tests for envdiff.deduplicator."""
import pytest

from envdiff.deduplicator import DedupeResult, deduplicate, to_env_string


SAMPLE = """
HOST=localhost
PORT=5432
HOST=production.example.com
DEBUG=true
PORT=9999
"""


def test_deduplicate_last_keeps_final_value():
    result = deduplicate(SAMPLE, keep="last")
    assert result.env["HOST"] == "production.example.com"
    assert result.env["PORT"] == "9999"


def test_deduplicate_first_keeps_initial_value():
    result = deduplicate(SAMPLE, keep="first")
    assert result.env["HOST"] == "localhost"
    assert result.env["PORT"] == "5432"


def test_duplicate_keys_recorded():
    result = deduplicate(SAMPLE)
    assert "HOST" in result.duplicates
    assert "PORT" in result.duplicates


def test_non_duplicate_key_not_in_duplicates():
    result = deduplicate(SAMPLE)
    assert "DEBUG" not in result.duplicates


def test_has_duplicates_true_when_dupes_exist():
    result = deduplicate(SAMPLE)
    assert result.has_duplicates is True


def test_has_duplicates_false_when_no_dupes():
    result = deduplicate("FOO=bar\nBAZ=qux\n")
    assert result.has_duplicates is False


def test_duplicate_count():
    result = deduplicate(SAMPLE)
    assert result.duplicate_count == 2


def test_no_duplicates_env_unchanged():
    text = "FOO=1\nBAR=2\nBAZ=3\n"
    result = deduplicate(text)
    assert result.env == {"FOO": "1", "BAR": "2", "BAZ": "3"}


def test_comments_and_blanks_ignored():
    text = "# comment\n\nFOO=bar\nFOO=baz\n"
    result = deduplicate(text)
    assert result.env["FOO"] == "baz"
    assert result.duplicates == ["FOO"]


def test_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate(SAMPLE, keep="middle")


def test_to_env_string_round_trip():
    result = deduplicate("A=1\nB=2\nA=3\n")
    output = to_env_string(result)
    assert "A=3" in output
    assert "B=2" in output
    # Only one A line
    assert output.count("A=") == 1


def test_to_env_string_ends_with_newline():
    result = deduplicate("X=1\n")
    assert to_env_string(result).endswith("\n")
