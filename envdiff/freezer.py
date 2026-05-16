"""Freeze an .env file by locking all values to their current state.

A frozen env file marks every key as immutable by appending a
# frozen comment marker, and records which keys were already frozen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string

_FROZEN_MARKER = "# frozen"


@dataclass
class FreezeResult:
    values: Dict[str, str]
    frozen_keys: List[str]
    already_frozen: List[str]


def frozen_count(result: FreezeResult) -> int:
    return len(result.frozen_keys)


def _is_frozen(line: str) -> bool:
    return line.rstrip().endswith(_FROZEN_MARKER)


def freeze_values(
    env_string: str,
    keys: Optional[List[str]] = None,
) -> FreezeResult:
    """Parse *env_string* and mark the requested *keys* as frozen.

    If *keys* is None every key is frozen.
    Returns a :class:`FreezeResult` with the resulting values dict and
    bookkeeping lists.
    """
    values = parse_env_string(env_string)
    target_keys = set(keys) if keys is not None else set(values)

    frozen_keys: List[str] = []
    already_frozen: List[str] = []

    raw_lines = env_string.splitlines()
    frozen_line_keys: set = set()
    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped and _is_frozen(raw):
            k = stripped.split("=", 1)[0].strip()
            frozen_line_keys.add(k)

    for k in values:
        if k not in target_keys:
            continue
        if k in frozen_line_keys:
            already_frozen.append(k)
        else:
            frozen_keys.append(k)

    return FreezeResult(
        values=values,
        frozen_keys=sorted(frozen_keys),
        already_frozen=sorted(already_frozen),
    )


def freeze_string(
    env_string: str,
    keys: Optional[List[str]] = None,
) -> str:
    """Return a new env string with frozen markers appended to target lines."""
    target_keys = set(keys) if keys is not None else None
    out_lines: List[str] = []
    for raw in env_string.splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if (target_keys is None or k in target_keys) and not _is_frozen(raw):
                raw = raw.rstrip() + "  " + _FROZEN_MARKER
        out_lines.append(raw)
    return "\n".join(out_lines)


def to_env_string(result: FreezeResult) -> str:
    """Serialise *result.values* back to a plain dotenv string (no markers)."""
    return "\n".join(f"{k}={v}" for k, v in result.values.items())
