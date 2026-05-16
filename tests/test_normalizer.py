"""Tests for envdiff.normalizer."""
import pytest

from envdiff.normalizer import (
    NormalizeResult,
    normalize_string,
    normalize_values,
    normalized_count,
    to_env_string,
)


def test_uppercase_keys_renames_lowercase():
    result = normalize_values({"db_host": "localhost"}, uppercase_keys=True)
    assert "DB_HOST" in result.values
    assert "db_host" not in result.values
    assert "DB_HOST" in result.uppercased


def test_uppercase_keys_disabled_preserves_case():
    result = normalize_values({"db_host": "localhost"}, uppercase_keys=False)
    assert "db_host" in result.values
    assert result.uppercased == []


def test_trim_values_strips_whitespace():
    result = normalize_values({"KEY": "  value  "}, trim_values=True)
    assert result.values["KEY"] == "value"
    assert "KEY" in result.trimmed


def test_trim_disabled_preserves_spaces():
    result = normalize_values({"KEY": "  value  "}, trim_values=False)
    assert result.values["KEY"] == "  value  "
    assert result.trimmed == []


def test_normalize_bool_true_variants():
    for raw in ("yes", "1", "on", "YES", "True"):
        result = normalize_values({"FLAG": raw}, normalize_bools=True)
        assert result.values["FLAG"] == "true", f"failed for {raw!r}"


def test_normalize_bool_false_variants():
    for raw in ("no", "0", "off", "NO", "False"):
        result = normalize_values({"FLAG": raw}, normalize_bools=True)
        assert result.values["FLAG"] == "false", f"failed for {raw!r}"


def test_bool_already_normalized_not_recorded():
    result = normalize_values({"FLAG": "true"}, normalize_bools=True)
    assert "FLAG" not in result.bool_normalized


def test_normalize_bools_disabled_preserves_value():
    result = normalize_values({"FLAG": "yes"}, normalize_bools=False)
    assert result.values["FLAG"] == "yes"
    assert result.bool_normalized == []


def test_normalized_count_deduplicates_across_lists():
    result = normalize_values(
        {"db_url": "  postgres://localhost  "},
        uppercase_keys=True,
        trim_values=True,
    )
    # DB_URL appears in both uppercased and trimmed; count should be 1
    assert normalized_count(result) == 1


def test_normalize_string_parses_and_normalizes():
    text = "db_host=localhost\nDEBUG=yes"
    result = normalize_string(text)
    assert result.values["DB_HOST"] == "localhost"
    assert result.values["DEBUG"] == "true"


def test_to_env_string_produces_valid_dotenv():
    result = NormalizeResult(values={"HOST": "localhost", "PORT": "5432"})
    out = to_env_string(result)
    assert "HOST=localhost" in out
    assert "PORT=5432" in out


def test_unchanged_value_not_in_any_list():
    result = normalize_values({"KEY": "value"}, uppercase_keys=True)
    assert "KEY" not in result.uppercased
    assert "KEY" not in result.trimmed
    assert "KEY" not in result.bool_normalized
