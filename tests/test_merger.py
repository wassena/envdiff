"""Tests for envdiff.merger."""
import pytest

from envdiff.merger import MergeResult, merge_files, merge_strings


# ---------------------------------------------------------------------------
# merge_strings helpers
# ---------------------------------------------------------------------------

ENV_A = "HOST=localhost\nPORT=5432\nDEBUG=true\n"
ENV_B = "PORT=9999\nSECRET=abc123\n"
ENV_C = "DEBUG=false\nSECRET=overridden\n"


def test_merge_strings_combines_all_keys():
    result = merge_strings(ENV_A, ENV_B)
    assert "HOST" in result.merged
    assert "PORT" in result.merged
    assert "SECRET" in result.merged


def test_merge_strings_later_wins():
    result = merge_strings(ENV_A, ENV_B)
    assert result.merged["PORT"] == "9999"


def test_merge_strings_no_conflict_key_preserved():
    result = merge_strings(ENV_A, ENV_B)
    assert result.merged["HOST"] == "localhost"
    assert result.merged["DEBUG"] == "true"


def test_merge_strings_overrides_recorded():
    result = merge_strings(ENV_A, ENV_B)
    assert "PORT" in result.overrides
    # The displaced value should be the original from ENV_A
    displaced_values = [v for _, v in result.overrides["PORT"]]
    assert "5432" in displaced_values


def test_merge_strings_three_sources():
    result = merge_strings(ENV_A, ENV_B, ENV_C)
    assert result.merged["DEBUG"] == "false"
    assert result.merged["SECRET"] == "overridden"
    assert result.override_count == 2  # PORT and SECRET and DEBUG — PORT + SECRET + DEBUG


def test_merge_strings_override_count():
    result = merge_strings(ENV_A, ENV_B)
    # Only PORT conflicts
    assert result.override_count == 1


def test_merge_strings_requires_two_sources():
    with pytest.raises(ValueError, match="at least two"):
        merge_strings(ENV_A)


# ---------------------------------------------------------------------------
# merge_files helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def env_files(tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(ENV_A)
    b.write_text(ENV_B)
    return str(a), str(b)


def test_merge_files_basic(env_files):
    a, b = env_files
    result = merge_files(a, b)
    assert isinstance(result, MergeResult)
    assert result.merged["SECRET"] == "abc123"
    assert result.merged["HOST"] == "localhost"


def test_merge_files_later_wins(env_files):
    a, b = env_files
    result = merge_files(a, b)
    assert result.merged["PORT"] == "9999"


def test_merge_files_missing_file_raises(tmp_path):
    a = tmp_path / "a.env"
    a.write_text(ENV_A)
    with pytest.raises(FileNotFoundError):
        merge_files(str(a), str(tmp_path / "nonexistent.env"))


def test_merge_files_requires_two_paths(env_files):
    a, _ = env_files
    with pytest.raises(ValueError, match="at least two"):
        merge_files(a)
