"""Snapshot support: save and load .env snapshots with metadata."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from envdiff.parser import parse_env_file

SNAPSHOT_VERSION = 1


def create_snapshot(env_path: str, label: Optional[str] = None) -> dict:
    """Parse an env file and wrap it in a snapshot envelope."""
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"env file not found: {env_path}")
    values: Dict[str, str] = parse_env_file(env_path)
    return {
        "version": SNAPSHOT_VERSION,
        "source": os.path.abspath(env_path),
        "label": label or os.path.basename(env_path),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "values": values,
    }


def save_snapshot(snapshot: dict, output_path: str) -> None:
    """Serialise a snapshot to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
        fh.write("\n")


def load_snapshot(snapshot_path: str) -> dict:
    """Load and validate a snapshot from a JSON file."""
    if not os.path.isfile(snapshot_path):
        raise FileNotFoundError(f"snapshot file not found: {snapshot_path}")
    with open(snapshot_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _validate_snapshot(data)
    return data


def snapshot_values(snapshot: dict) -> Dict[str, str]:
    """Extract the key/value mapping from a snapshot."""
    return dict(snapshot["values"])


def _validate_snapshot(data: dict) -> None:
    required = {"version", "source", "label", "captured_at", "values"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"snapshot missing fields: {sorted(missing)}")
    if not isinstance(data["values"], dict):
        raise ValueError("snapshot 'values' must be a JSON object")
