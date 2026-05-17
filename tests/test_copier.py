"""Tests for envdiff.copier."""
import pytest

from envdiff.copier import (
    CopyResult,
    copy_keys,
    copy_string,
    copied_count,
    to_env_string,
)


SOURCE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"APP": "myapp", "PORT": "3000"}


# ---------------------------------------------------------------------------
# copy_keys
# ---------------------------------------------------------------------------

def test_copy_all_keys_by_default():
    result = copy_keys(SOURCE, TARGET)
    assert result.values["HOST"] == "localhost"
    assert result.values["DEBUG"] == "true"


def test_copy_preserves_target_only_keys():
    result = copy_keys(SOURCE, TARGET)
    assert result.values["APP"] == "myapp"


def test_copy_specific_keys_only():
    result = copy_keys(SOURCE, TARGET, keys=["HOST"])
    assert "HOST" in result.values
    assert "DEBUG" not in result.values


def test_copy_records_copied_keys():
    result = copy_keys(SOURCE, TARGET, keys=["HOST", "PORT"])
    assert "HOST" in result.copied
    assert "PORT" in result.copied


def test_missing_key_goes_to_skipped():
    result = copy_keys(SOURCE, TARGET, keys=["MISSING"])
    assert "MISSING" in result.skipped
    assert "MISSING" not in result.values


def test_overwrite_true_replaces_existing():
    result = copy_keys(SOURCE, TARGET, keys=["PORT"], overwrite=True)
    assert result.values["PORT"] == "5432"


def test_overwrite_false_preserves_existing():
    result = copy_keys(SOURCE, TARGET, keys=["PORT"], overwrite=False)
    assert result.values["PORT"] == "3000"
    assert "PORT" in result.skipped


def test_prefix_prepended_to_dest_key():
    result = copy_keys(SOURCE, {}, keys=["HOST"], prefix="DB_")
    assert "DB_HOST" in result.values
    assert result.values["DB_HOST"] == "localhost"
    assert "HOST" not in result.values


def test_copied_count():
    result = copy_keys(SOURCE, TARGET, keys=["HOST", "MISSING"])
    assert copied_count(result) == 1


def test_source_not_mutated():
    original = dict(SOURCE)
    copy_keys(SOURCE, TARGET)
    assert SOURCE == original


def test_target_not_mutated():
    original = dict(TARGET)
    copy_keys(SOURCE, TARGET)
    assert TARGET == original


# ---------------------------------------------------------------------------
# copy_string
# ---------------------------------------------------------------------------

def test_copy_string_parses_and_copies():
    src = "HOST=db.local\nPORT=5432\n"
    tgt = "APP=web\n"
    result = copy_string(src, tgt, keys=["HOST"])
    assert result.values["HOST"] == "db.local"
    assert result.values["APP"] == "web"


def test_copy_string_with_prefix():
    src = "USER=admin\n"
    tgt = ""
    result = copy_string(src, tgt, prefix="DB_")
    assert "DB_USER" in result.values


# ---------------------------------------------------------------------------
# to_env_string
# ---------------------------------------------------------------------------

def test_to_env_string_format():
    result = CopyResult(values={"A": "1", "B": "2"})
    output = to_env_string(result)
    assert "A=1\n" in output
    assert "B=2\n" in output
