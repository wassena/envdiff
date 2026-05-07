"""Tests for envdiff.templater."""
import pytest

from envdiff.templater import (
    build_template,
    template_from_string,
    TemplateResult,
)


SAMPLE = "DB_HOST=localhost\nDB_PASS=secret\nAPP_DEBUG=true\n"


def test_build_template_redacts_all_by_default():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret"}
    result = build_template(env)
    assert result.template["DB_HOST"] == "<REDACTED>"
    assert result.template["DB_PASS"] == "<REDACTED>"


def test_build_template_keeps_specified_keys():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret"}
    result = build_template(env, keep_values=["DB_HOST"])
    assert result.template["DB_HOST"] == "localhost"
    assert result.template["DB_PASS"] == "<REDACTED>"


def test_build_template_no_redact_preserves_all():
    env = {"DB_HOST": "localhost", "DB_PASS": "secret"}
    result = build_template(env, redact=False)
    assert result.template["DB_HOST"] == "localhost"
    assert result.template["DB_PASS"] == "secret"


def test_build_template_custom_placeholder():
    env = {"KEY": "value"}
    result = build_template(env, placeholder="CHANGE_ME")
    assert result.template["KEY"] == "CHANGE_ME"


def test_build_template_preserves_key_order():
    env = {"Z": "1", "A": "2", "M": "3"}
    result = build_template(env)
    assert result.keys == ["Z", "A", "M"]


def test_template_result_to_env_string():
    result = TemplateResult(keys=["A", "B"], template={"A": "<REDACTED>", "B": "<REDACTED>"})
    output = result.to_env_string()
    assert "A=<REDACTED>" in output
    assert "B=<REDACTED>" in output
    assert output.endswith("\n")


def test_template_result_empty_to_env_string():
    result = TemplateResult()
    assert result.to_env_string() == ""


def test_template_from_string_basic():
    result = template_from_string(SAMPLE)
    assert set(result.keys) == {"DB_HOST", "DB_PASS", "APP_DEBUG"}
    for v in result.template.values():
        assert v == "<REDACTED>"


def test_template_from_string_keep():
    result = template_from_string(SAMPLE, keep_values=["APP_DEBUG"])
    assert result.template["APP_DEBUG"] == "true"
    assert result.template["DB_PASS"] == "<REDACTED>"


def test_template_from_string_no_redact():
    result = template_from_string(SAMPLE, redact=False)
    assert result.template["DB_HOST"] == "localhost"
    assert result.template["DB_PASS"] == "secret"
