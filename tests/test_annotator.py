"""Tests for envdiff.annotator."""
from __future__ import annotations

import pytest

from envdiff.annotator import (
    AnnotateResult,
    annotate_string,
    annotate_values,
    annotated_count,
    to_env_string,
)


SAMPLE = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


def test_annotate_values_adds_comment():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = annotate_values(env, {"DB_HOST": "primary database host"})
    assert result.values["DB_HOST"] == "localhost  # primary database host"


def test_annotate_values_unchanged_key_untouched():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = annotate_values(env, {"DB_HOST": "host"})
    assert result.values["DB_PORT"] == "5432"


def test_annotate_values_missing_key_skipped():
    env = {"DB_HOST": "localhost"}
    result = annotate_values(env, {"MISSING": "not here"})
    assert "MISSING" not in result.values
    assert result.annotated == []


def test_annotate_values_records_annotated_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = annotate_values(env, {"A": "first", "C": "third"})
    assert set(result.annotated) == {"A", "C"}


def test_annotated_count():
    env = {"X": "1", "Y": "2"}
    result = annotate_values(env, {"X": "ex", "Y": "why"})
    assert annotated_count(result) == 2


def test_annotate_values_no_overwrite_preserves_existing_comment():
    env = {"KEY": "val  # old comment"}
    result = annotate_values(env, {"KEY": "new comment"}, overwrite=False)
    assert result.values["KEY"] == "val  # old comment"
    assert result.annotated == []


def test_annotate_values_overwrite_replaces_existing_comment():
    env = {"KEY": "val  # old comment"}
    result = annotate_values(env, {"KEY": "new comment"}, overwrite=True)
    assert result.values["KEY"] == "val  # new comment"
    assert "KEY" in result.annotated


def test_annotate_string_parses_source():
    result = annotate_string(SAMPLE, {"DB_PORT": "TCP port"})
    assert "DB_PORT" in result.values
    assert result.values["DB_PORT"] == "5432  # TCP port"


def test_to_env_string_format():
    env = {"A": "1  # note", "B": "2"}
    result = AnnotateResult(values=env, annotations={"A": "note"}, annotated=["A"])
    output = to_env_string(result)
    assert "A=1  # note" in output
    assert "B=2" in output


def test_to_env_string_ends_with_newline():
    env = {"K": "v"}
    result = AnnotateResult(values=env, annotations={}, annotated=[])
    assert to_env_string(result).endswith("\n")


def test_annotate_empty_env_returns_empty():
    result = annotate_values({}, {"KEY": "comment"})
    assert result.values == {}
    assert result.annotated == []
