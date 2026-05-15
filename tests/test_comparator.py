"""Tests for envdiff.comparator."""
import pytest

from envdiff.comparator import (
    CompareResult,
    compare_strings,
    similarity_score,
    total_keys,
)

ENV_A = """HOST=localhost
PORT=5432
DEBUG=true
SECRET=abc
"""

ENV_B = """HOST=localhost
PORT=5433
NEW_KEY=hello
"""


@pytest.fixture
def result() -> CompareResult:
    return compare_strings(ENV_A, ENV_B, label_a="A", label_b="B")


def test_common_key_same_value(result):
    assert "HOST" in result.common
    assert result.common["HOST"] == "localhost"


def test_changed_key_captured(result):
    assert "PORT" in result.changed
    assert result.changed["PORT"] == ("5432", "5433")


def test_only_in_a(result):
    assert "DEBUG" in result.only_in_a
    assert "SECRET" in result.only_in_a


def test_only_in_b(result):
    assert "NEW_KEY" in result.only_in_b


def test_total_keys(result):
    # HOST (common), PORT (changed), DEBUG, SECRET (only_a), NEW_KEY (only_b)
    assert total_keys(result) == 5


def test_similarity_score_partial(result):
    score = similarity_score(result)
    assert 0.0 < score < 1.0


def test_similarity_score_identical():
    env = "A=1\nB=2\n"
    r = compare_strings(env, env)
    assert similarity_score(r) == 1.0


def test_similarity_score_empty():
    r = compare_strings("", "")
    assert similarity_score(r) == 1.0


def test_similarity_score_no_overlap():
    r = compare_strings("A=1\n", "B=2\n")
    assert similarity_score(r) == 0.0


def test_labels_stored(result):
    assert result.source_a == "A"
    assert result.source_b == "B"


def test_changed_not_in_common(result):
    assert "PORT" not in result.common


def test_only_in_a_not_in_only_b(result):
    assert set(result.only_in_a).isdisjoint(set(result.only_in_b))
