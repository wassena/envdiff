"""Tests for envdiff.masker."""
import pytest

from envdiff.masker import (
    DEFAULT_MASK,
    MaskResult,
    mask_string,
    mask_values,
    to_masked_env_string,
)


SAMPLE = """\
APP_NAME=myapp
DB_PASSWORD=supersecret
API_KEY=abc123
DEBUG=true
SECRET_KEY=topsecret
PORT=8080
"""


def test_mask_values_replaces_sensitive_keys():
    env = {"DB_PASSWORD": "s3cr3t", "APP_NAME": "app"}
    result = mask_values(env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["APP_NAME"] == "app"


def test_mask_values_records_masked_keys():
    env = {"API_KEY": "key", "TOKEN": "tok", "HOST": "localhost"}
    result = mask_values(env)
    assert "API_KEY" in result.masked_keys
    assert "TOKEN" in result.masked_keys
    assert "HOST" not in result.masked_keys


def test_mask_values_custom_mask_string():
    env = {"SECRET_KEY": "val"}
    result = mask_values(env, mask="REDACTED")
    assert result.masked["SECRET_KEY"] == "REDACTED"


def test_mask_values_custom_pattern():
    env = {"CUSTOM_SENSITIVE": "val", "NORMAL": "ok"}
    result = mask_values(env, patterns=[r"CUSTOM_.*"])
    assert result.masked["CUSTOM_SENSITIVE"] == DEFAULT_MASK
    assert result.masked["NORMAL"] == "ok"


def test_mask_string_parses_and_masks():
    result = mask_string(SAMPLE)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["API_KEY"] == DEFAULT_MASK
    assert result.masked["SECRET_KEY"] == DEFAULT_MASK
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_mask_count():
    result = mask_string(SAMPLE)
    assert result.mask_count == 3


def test_original_keys_preserved_in_order():
    result = mask_string(SAMPLE)
    assert list(result.original_keys) == [
        "APP_NAME", "DB_PASSWORD", "API_KEY", "DEBUG", "SECRET_KEY", "PORT"
    ]


def test_to_masked_env_string_format():
    result = mask_string("KEY=value\nSECRET_KEY=hidden\n")
    output = to_masked_env_string(result)
    assert "KEY=value" in output
    assert f"SECRET_KEY={DEFAULT_MASK}" in output


def test_to_masked_env_string_ends_with_newline():
    result = mask_string("A=1\n")
    assert to_masked_env_string(result).endswith("\n")


def test_empty_env_mask_count_is_zero():
    result = mask_values({})
    assert result.mask_count == 0
    assert result.masked == {}
