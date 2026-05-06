"""Tests for envdiff.formatter."""

import json
import pytest
from envdiff.differ import diff_envs
from envdiff.formatter import render, format_text, format_json, format_dotenv


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "prod.example.com", "DB_PORT": "5432", "API_KEY": "xyz"}


@pytest.fixture()
def result():
    return diff_envs(ENV_A, ENV_B)


def test_format_text_shows_missing_in_b(result):
    output = format_text(result, "local", "prod")
    assert "Keys in [local] but missing in [prod]" in output
    assert "SECRET=abc" in output


def test_format_text_shows_missing_in_a(result):
    output = format_text(result, "local", "prod")
    assert "Keys in [prod] but missing in [local]" in output
    assert "API_KEY=xyz" in output


def test_format_text_shows_changed(result):
    output = format_text(result, "local", "prod")
    assert "Changed values:" in output
    assert "DB_HOST" in output
    assert "localhost" in output
    assert "prod.example.com" in output


def test_format_text_no_differences():
    env = {"KEY": "value"}
    result = diff_envs(env, env)
    output = format_text(result)
    assert "No differences found." in output


def test_format_json_structure(result):
    output = format_json(result, "local", "prod")
    data = json.loads(output)
    assert "missing_in_prod" in data
    assert "missing_in_local" in data
    assert "changed" in data
    assert data["missing_in_prod"]["SECRET"] == "abc"
    assert data["missing_in_local"]["API_KEY"] == "xyz"
    assert data["changed"]["DB_HOST"]["local"] == "localhost"
    assert data["changed"]["DB_HOST"]["prod"] == "prod.example.com"


def test_format_dotenv_contains_b_values(result):
    output = format_dotenv(result)
    lines = output.splitlines()
    assert "API_KEY=xyz" in lines
    assert "DB_HOST=prod.example.com" in lines
    # SECRET is only missing in B, not missing in A — should NOT appear
    assert not any(line.startswith("SECRET=") for line in lines)


def test_render_dispatches_to_json(result):
    output = render(result, fmt="json", env_a_label="a", env_b_label="b")
    data = json.loads(output)
    assert isinstance(data, dict)


def test_render_dispatches_to_dotenv(result):
    output = render(result, fmt="dotenv")
    assert "=" in output


def test_render_default_is_text(result):
    output = render(result)
    assert "Changed values:" in output or "No differences found." in output
