"""Sanitize .env values by stripping control characters and enforcing safe encoding."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_LEADING_TRAILING_SPACE_RE = re.compile(r"^\s+|\s+$")


@dataclass
class SanitizeResult:
    values: Dict[str, str]
    sanitized: List[str] = field(default_factory=list)


def sanitized_count(result: SanitizeResult) -> int:
    return len(result.sanitized)


def _sanitize_value(value: str, strip_whitespace: bool = True) -> tuple[str, bool]:
    """Return (cleaned_value, was_changed)."""
    cleaned = _CONTROL_RE.sub("", value)
    if strip_whitespace:
        cleaned = _LEADING_TRAILING_SPACE_RE.sub("", cleaned)
    return cleaned, cleaned != value


def sanitize_values(
    env: Dict[str, str],
    *,
    strip_whitespace: bool = True,
) -> SanitizeResult:
    """Sanitize all values in *env*, returning a SanitizeResult."""
    out: Dict[str, str] = {}
    changed: List[str] = []
    for key, value in env.items():
        cleaned, was_changed = _sanitize_value(value, strip_whitespace=strip_whitespace)
        out[key] = cleaned
        if was_changed:
            changed.append(key)
    return SanitizeResult(values=out, sanitized=changed)


def sanitize_string(
    text: str,
    *,
    strip_whitespace: bool = True,
) -> SanitizeResult:
    """Parse *text* as a .env document and sanitize its values."""
    env = parse_env_string(text)
    return sanitize_values(env, strip_whitespace=strip_whitespace)


def to_env_string(result: SanitizeResult) -> str:
    """Serialise a SanitizeResult back to .env format."""
    lines = [f"{k}={v}" for k, v in result.values.items()]
    return "\n".join(lines) + ("\n" if lines else "")
