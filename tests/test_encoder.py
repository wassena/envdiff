"""Tests for envdiff.encoder."""
import base64
import urllib.parse

import pytest

from envdiff.encoder import (
    EncodeResult,
    encode_string,
    encode_values,
    encoded_count,
    to_env_string,
)


@pytest.fixture()
def sample_env():
    return {"DB_PASS": "s3cr3t", "API_KEY": "abc123", "DEBUG": "true"}


def test_encode_all_keys_base64(sample_env):
    result = encode_values(sample_env, scheme="base64")
    assert result.values["DB_PASS"] == base64.b64encode(b"s3cr3t").decode()
    assert result.values["API_KEY"] == base64.b64encode(b"abc123").decode()
    assert result.values["DEBUG"] == base64.b64encode(b"true").decode()


def test_encode_specific_keys_only(sample_env):
    result = encode_values(sample_env, keys=["DB_PASS"], scheme="base64")
    assert result.values["DB_PASS"] == base64.b64encode(b"s3cr3t").decode()
    assert result.values["API_KEY"] == "abc123"
    assert result.values["DEBUG"] == "true"


def test_encoded_keys_recorded(sample_env):
    result = encode_values(sample_env, keys=["DB_PASS", "API_KEY"], scheme="base64")
    assert "DB_PASS" in result.encoded_keys
    assert "API_KEY" in result.encoded_keys
    assert "DEBUG" not in result.encoded_keys


def test_encoded_count(sample_env):
    result = encode_values(sample_env, keys=["DB_PASS"], scheme="base64")
    assert encoded_count(result) == 1


def test_urlenc_scheme(sample_env):
    result = encode_values(sample_env, keys=["DB_PASS"], scheme="urlenc")
    assert result.values["DB_PASS"] == urllib.parse.quote("s3cr3t", safe="")


def test_urlenc_with_special_chars():
    env = {"SECRET": "p@ss w0rd!"}
    result = encode_values(env, scheme="urlenc")
    assert result.values["SECRET"] == "p%40ss%20w0rd%21"


def test_unknown_scheme_raises(sample_env):
    with pytest.raises(ValueError, match="Unknown encoding scheme"):
        encode_values(sample_env, scheme="rot13")


def test_skip_already_encoded_base64():
    already = base64.b64encode(b"s3cr3t").decode()
    env = {"DB_PASS": already}
    result = encode_values(env, scheme="base64", skip_already_encoded=True)
    assert result.values["DB_PASS"] == already
    assert "DB_PASS" in result.skipped_keys
    assert "DB_PASS" not in result.encoded_keys


def test_encode_string_parses_and_encodes():
    text = "DB_PASS=secret\nDEBUG=true"
    result = encode_string(text, keys=["DB_PASS"], scheme="base64")
    assert result.values["DB_PASS"] == base64.b64encode(b"secret").decode()
    assert result.values["DEBUG"] == "true"


def test_to_env_string_format(sample_env):
    result = encode_values(sample_env, keys=["DEBUG"], scheme="base64")
    output = to_env_string(result)
    assert "DEBUG=" in output
    assert "DB_PASS=s3cr3t" in output


def test_empty_value_encoded():
    env = {"EMPTY": ""}
    result = encode_values(env, scheme="base64")
    assert result.values["EMPTY"] == base64.b64encode(b"").decode()
    assert encoded_count(result) == 1
