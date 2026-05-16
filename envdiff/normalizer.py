"""Normalize .env values: uppercase keys, trim whitespace, unify booleans."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class NormalizeResult:
    values: Dict[str, str]
    uppercased: List[str] = field(default_factory=list)
    trimmed: List[str] = field(default_factory=list)
    bool_normalized: List[str] = field(default_factory=list)


def normalized_count(result: NormalizeResult) -> int:
    seen = set(result.uppercased) | set(result.trimmed) | set(result.bool_normalized)
    return len(seen)


def normalize_values(
    values: Dict[str, str],
    *,
    uppercase_keys: bool = True,
    trim_values: bool = True,
    normalize_bools: bool = True,
) -> NormalizeResult:
    out: Dict[str, str] = {}
    uppercased: List[str] = []
    trimmed: List[str] = []
    bool_normalized: List[str] = []

    for raw_key, raw_val in values.items():
        key = raw_key.upper() if uppercase_keys and raw_key != raw_key.upper() else raw_key
        if key != raw_key:
            uppercased.append(key)

        val = raw_val
        if trim_values:
            stripped = val.strip()
            if stripped != val:
                trimmed.append(key)
                val = stripped

        if normalize_bools:
            lower = val.lower()
            if lower in _BOOL_TRUE and val != "true":
                bool_normalized.append(key)
                val = "true"
            elif lower in _BOOL_FALSE and val != "false":
                bool_normalized.append(key)
                val = "false"

        out[key] = val

    return NormalizeResult(
        values=out,
        uppercased=uppercased,
        trimmed=trimmed,
        bool_normalized=bool_normalized,
    )


def normalize_string(
    text: str,
    *,
    uppercase_keys: bool = True,
    trim_values: bool = True,
    normalize_bools: bool = True,
) -> NormalizeResult:
    values = parse_env_string(text)
    return normalize_values(
        values,
        uppercase_keys=uppercase_keys,
        trim_values=trim_values,
        normalize_bools=normalize_bools,
    )


def to_env_string(result: NormalizeResult) -> str:
    return "\n".join(f"{k}={v}" for k, v in result.values.items())
