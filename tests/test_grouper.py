"""Tests for envdiff.grouper."""
from __future__ import annotations

import pytest

from envdiff.grouper import (
    GroupResult,
    _extract_prefix,
    group_keys,
    group_from_string,
    to_grouped_text,
)


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "APP_ENV": "production",
    "PORT": "8080",
}


def test_extract_prefix_returns_first_segment():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_separator_returns_none():
    assert _extract_prefix("PORT") is None


def test_extract_prefix_custom_separator():
    assert _extract_prefix("DB.HOST", ".") == "DB"


def test_group_keys_creates_expected_groups():
    result = group_keys(SAMPLE)
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert "APP" in result.groups


def test_group_keys_correct_members():
    result = group_keys(SAMPLE)
    assert set(result.groups["DB"].keys()) == {"DB_HOST", "DB_PORT"}


def test_group_keys_no_prefix_goes_to_ungrouped():
    result = group_keys(SAMPLE)
    assert "PORT" in result.ungrouped


def test_group_keys_total_keys_matches_input():
    result = group_keys(SAMPLE)
    assert result.total_keys() == len(SAMPLE)


def test_min_group_size_moves_small_groups_to_ungrouped():
    result = group_keys(SAMPLE, min_group_size=2)
    # APP has only 1 key, so it should fall into ungrouped
    assert "APP" not in result.groups
    assert "APP_ENV" in result.ungrouped


def test_min_group_size_keeps_large_groups():
    result = group_keys(SAMPLE, min_group_size=2)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_all_prefixes_sorted():
    result = group_keys(SAMPLE)
    prefixes = result.all_prefixes()
    assert prefixes == sorted(prefixes)


def test_group_from_string_parses_and_groups():
    text = "DB_HOST=localhost\nDB_PORT=5432\nPORT=8080\n"
    result = group_from_string(text)
    assert "DB" in result.groups
    assert "PORT" in result.ungrouped


def test_to_grouped_text_contains_section_headers():
    result = group_keys(SAMPLE)
    text = to_grouped_text(result)
    assert "# [DB]" in text
    assert "# [AWS]" in text


def test_to_grouped_text_contains_key_value_pairs():
    result = group_keys(SAMPLE)
    text = to_grouped_text(result)
    assert "DB_HOST=localhost" in text


def test_to_grouped_text_ungrouped_section():
    result = group_keys(SAMPLE)
    text = to_grouped_text(result)
    assert "# [ungrouped]" in text
    assert "PORT=8080" in text


def test_empty_env_returns_empty_result():
    result = group_keys({})
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.total_keys() == 0
