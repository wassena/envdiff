"""Trim keys and/or values in a .env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string


@dataclass
class TrimResult:
    values: Dict[str, str]
    trimmed_keys: List[str] = field(default_factory=list)
    trimmed_values: List[str] = field(default_factory=list)


def trimmed_count(result: TrimResult) -> int:
    """Total number of entries where any trimming occurred."""
    return len(set(result.trimmed_keys) | set(result.trimmed_values))


def trim_values(
    env: Dict[str, str],
    *,
    trim_keys: bool = False,
    trim_values: bool = True,
) -> TrimResult:
    """Return a new mapping with keys and/or values stripped of whitespace.

    Args:
        env: Source key/value mapping.
        trim_keys: When *True*, strip whitespace from key names.
        trim_values: When *True* (default), strip whitespace from values.

    Returns:
        :class:`TrimResult` with the cleaned mapping and change lists.
    """
    out: Dict[str, str] = {}
    changed_keys: List[str] = []
    changed_values: List[str] = []

    for raw_key, raw_value in env.items():
        new_key = raw_key.strip() if trim_keys else raw_key
        new_value = raw_value.strip() if trim_values else raw_value

        if new_key != raw_key:
            changed_keys.append(raw_key)
        if new_value != raw_value:
            changed_values.append(new_key)

        out[new_key] = new_value

    return TrimResult(
        values=out,
        trimmed_keys=changed_keys,
        trimmed_values=changed_values,
    )


def trim_string(
    text: str,
    *,
    trim_keys: bool = False,
    trim_values: bool = True,
) -> TrimResult:
    """Parse *text* as a .env string and trim it."""
    env = parse_env_string(text)
    return trim_values(env, trim_keys=trim_keys, trim_values=trim_values)


def to_env_string(result: TrimResult) -> str:
    """Serialise a :class:`TrimResult` back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in result.values.items())
