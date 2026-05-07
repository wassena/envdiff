"""Tests for envdiff.snapshot module."""

import json
import os
import pytest

from envdiff.snapshot import (
    create_snapshot,
    load_snapshot,
    save_snapshot,
    snapshot_values,
    SNAPSHOT_VERSION,
)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n")
    return str(p)


def test_create_snapshot_has_required_fields(env_file):
    snap = create_snapshot(env_file)
    assert snap["version"] == SNAPSHOT_VERSION
    assert "captured_at" in snap
    assert snap["values"]["DB_HOST"] == "localhost"
    assert snap["values"]["DB_PORT"] == "5432"


def test_create_snapshot_custom_label(env_file):
    snap = create_snapshot(env_file, label="production-2024")
    assert snap["label"] == "production-2024"


def test_create_snapshot_missing_file():
    with pytest.raises(FileNotFoundError):
        create_snapshot("/no/such/file.env")


def test_save_and_load_roundtrip(env_file, tmp_path):
    snap = create_snapshot(env_file)
    out = str(tmp_path / "snap.json")
    save_snapshot(snap, out)
    assert os.path.isfile(out)
    loaded = load_snapshot(out)
    assert loaded["values"] == snap["values"]


def test_load_snapshot_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(str(tmp_path / "ghost.json"))


def test_load_snapshot_invalid_missing_field(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"version": 1, "values": {}}))
    with pytest.raises(ValueError, match="missing fields"):
        load_snapshot(str(bad))


def test_load_snapshot_values_not_dict(tmp_path):
    bad = tmp_path / "bad2.json"
    bad.write_text(json.dumps({
        "version": 1, "source": "x", "label": "x",
        "captured_at": "now", "values": ["not", "a", "dict"]
    }))
    with pytest.raises(ValueError, match="must be a JSON object"):
        load_snapshot(str(bad))


def test_snapshot_values_returns_copy(env_file):
    snap = create_snapshot(env_file)
    vals = snapshot_values(snap)
    vals["INJECTED"] = "yes"
    assert "INJECTED" not in snap["values"]
