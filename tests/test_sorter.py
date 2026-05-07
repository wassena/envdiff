"""Tests for envdiff.sorter."""
import textwrap

import pytest

from envdiff.sorter import SortResult, sort_keys, to_sorted_env_string, sort_env_file


@pytest.fixture()
def sample_env() -> dict[str, str]:
    return {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


# ---------------------------------------------------------------------------
# sort_keys
# ---------------------------------------------------------------------------

def test_sort_keys_alphabetical(sample_env):
    result = sort_keys(sample_env)
    assert result.sorted_order == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_reverse(sample_env):
    result = sort_keys(sample_env, reverse=True)
    assert result.sorted_order == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_keys_already_sorted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_keys(env)
    assert result.is_sorted is True
    assert result.moved == []


def test_sort_keys_not_sorted(sample_env):
    result = sort_keys(sample_env)
    assert result.is_sorted is False


def test_sort_keys_custom_order(sample_env):
    result = sort_keys(sample_env, key_order=["MANGO", "ZEBRA"])
    # MANGO and ZEBRA first, then APPLE (remainder sorted)
    assert result.sorted_order == ["MANGO", "ZEBRA", "APPLE"]


def test_sort_keys_custom_order_unknown_keys_ignored(sample_env):
    result = sort_keys(sample_env, key_order=["GHOST", "APPLE"])
    # GHOST not in env, APPLE first, then remainder
    assert result.sorted_order[0] == "APPLE"
    assert "GHOST" not in result.sorted_order


def test_sort_keys_original_order_preserved(sample_env):
    result = sort_keys(sample_env)
    assert result.original_order == ["ZEBRA", "APPLE", "MANGO"]


# ---------------------------------------------------------------------------
# to_sorted_env_string
# ---------------------------------------------------------------------------

def test_to_sorted_env_string_output(sample_env):
    output = to_sorted_env_string(sample_env)
    assert output == "APPLE=2\nMANGO=3\nZEBRA=1\n"


def test_to_sorted_env_string_empty():
    assert to_sorted_env_string({}) == ""


def test_to_sorted_env_string_custom_order(sample_env):
    output = to_sorted_env_string(sample_env, key_order=["ZEBRA", "APPLE", "MANGO"])
    assert output == "ZEBRA=1\nAPPLE=2\nMANGO=3\n"


# ---------------------------------------------------------------------------
# sort_env_file
# ---------------------------------------------------------------------------

def test_sort_env_file(tmp_path, sample_env):
    env_file = tmp_path / ".env"
    env_file.write_text("ZEBRA=1\nAPPLE=2\nMANGO=3\n")

    result, content = sort_env_file(str(env_file))
    assert result.sorted_order == ["APPLE", "MANGO", "ZEBRA"]
    assert content == "APPLE=2\nMANGO=3\nZEBRA=1\n"


def test_sort_env_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        sort_env_file(str(tmp_path / "nonexistent.env"))
