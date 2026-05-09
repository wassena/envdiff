"""Tests for envdiff.extractor."""
import pytest

from envdiff.extractor import (
    ExtractResult,
    extract_from_string,
    extract_keys,
    to_env_string,
)

ENV = {
    "APP_NAME": "myapp",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "s3cr3t",
}


def test_extract_keys_returns_only_requested():
    result = extract_keys(ENV, ["APP_NAME", "DB_HOST"])
    assert result.extracted == {"APP_NAME": "myapp", "DB_HOST": "localhost"}


def test_extract_keys_missing_recorded():
    result = extract_keys(ENV, ["APP_NAME", "MISSING_KEY"])
    assert "MISSING_KEY" in result.missing
    assert "MISSING_KEY" not in result.extracted


def test_extract_keys_no_missing_when_all_present():
    result = extract_keys(ENV, ["DB_HOST", "DB_PORT"])
    assert result.missing == []


def test_extract_keys_default_fills_absent_keys():
    result = extract_keys(ENV, ["APP_NAME", "NOT_THERE"], default="CHANGEME")
    assert result.extracted["NOT_THERE"] == "CHANGEME"
    assert result.missing == []


def test_extract_keys_default_does_not_override_existing():
    result = extract_keys(ENV, ["APP_NAME"], default="CHANGEME")
    assert result.extracted["APP_NAME"] == "myapp"


def test_found_count():
    result = extract_keys(ENV, ["APP_NAME", "DB_HOST", "NOPE"])
    assert result.found_count == 2


def test_missing_count():
    result = extract_keys(ENV, ["APP_NAME", "NOPE1", "NOPE2"])
    assert result.missing_count == 2


def test_source_keys_reflects_input_env():
    result = extract_keys(ENV, ["APP_NAME"])
    assert set(result.source_keys) == set(ENV.keys())


def test_extract_from_string_parses_and_extracts():
    text = "APP_NAME=myapp\nDB_HOST=localhost\nSECRET_KEY=s3cr3t\n"
    result = extract_from_string(text, ["APP_NAME", "SECRET_KEY"])
    assert result.extracted == {"APP_NAME": "myapp", "SECRET_KEY": "s3cr3t"}
    assert result.missing == []


def test_extract_from_string_missing_key():
    text = "FOO=bar\n"
    result = extract_from_string(text, ["FOO", "BAZ"])
    assert "BAZ" in result.missing


def test_to_env_string_format():
    result = ExtractResult(
        extracted={"A": "1", "B": "2"},
        missing=[],
        source_keys=["A", "B"],
    )
    output = to_env_string(result)
    assert "A=1" in output
    assert "B=2" in output
    assert output.endswith("\n")


def test_to_env_string_empty_result():
    result = ExtractResult(extracted={}, missing=["X"], source_keys=[])
    assert to_env_string(result) == ""
