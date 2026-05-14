"""Type-casting utilities for .env values.

Infers and casts string values from .env files into Python native types
(bool, int, float, or str) and reports what was cast.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from envdiff.parser import parse_env_file, parse_env_string

_TRUE_VALUES = {"true", "yes", "1", "on"}
_FALSE_VALUES = {"false", "no", "0", "off"}


@dataclass
class CastResult:
    values: Dict[str, Any]
    casts: Dict[str, str]  # key -> inferred type name
    source: str = ""


def cast_count(result: CastResult) -> int:
    """Number of keys whose type differs from plain str."""
    return sum(1 for t in result.casts.values() if t != "str")


def _infer(value: str) -> Tuple[Any, str]:
    """Return (cast_value, type_name) for *value*."""
    if value.lower() in _TRUE_VALUES:
        return True, "bool"
    if value.lower() in _FALSE_VALUES:
        return False, "bool"
    try:
        return int(value), "int"
    except ValueError:
        pass
    try:
        return float(value), "float"
    except ValueError:
        pass
    return value, "str"


def cast_values(env: Dict[str, str], source: str = "") -> CastResult:
    """Cast all values in *env* to their inferred Python types."""
    values: Dict[str, Any] = {}
    casts: Dict[str, str] = {}
    for key, raw in env.items():
        val, typename = _infer(raw)
        values[key] = val
        casts[key] = typename
    return CastResult(values=values, casts=casts, source=source)


def cast_string(text: str, source: str = "") -> CastResult:
    """Parse *text* as a .env string then cast all values."""
    env = parse_env_string(text)
    return cast_values(env, source=source)


def cast_file(path: str) -> CastResult:
    """Parse the .env file at *path* then cast all values."""
    env = parse_env_file(path)
    return cast_values(env, source=path)


def summary(result: CastResult) -> List[str]:
    """Human-readable lines describing each non-str cast."""
    lines = []
    for key, typename in result.casts.items():
        if typename != "str":
            lines.append(f"{key}: {result.values[key]!r} ({typename})")
    return lines
