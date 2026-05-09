"""Redact sensitive values from parsed env dicts before display or export."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_REDACT_CHAR = "*"
DEFAULT_REDACT_LENGTH = 8


@dataclass
class RedactResult:
    redacted: Dict[str, str]
    redacted_keys: List[str]
    original_keys: List[str]

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)


def _redact_value(
    value: str,
    char: str = DEFAULT_REDACT_CHAR,
    length: int = DEFAULT_REDACT_LENGTH,
    partial: bool = False,
) -> str:
    """Return a redacted representation of *value*.

    When *partial* is True the first two and last two characters are kept
    (useful for debugging) provided the value is long enough.
    """
    if partial and len(value) > 6:
        return value[:2] + char * (length - 4) + value[-2:]
    return char * length


def redact_values(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    *,
    char: str = DEFAULT_REDACT_CHAR,
    length: int = DEFAULT_REDACT_LENGTH,
    partial: bool = False,
) -> RedactResult:
    """Redact *keys* inside *env*, returning a :class:`RedactResult`.

    If *keys* is ``None`` every key is redacted.
    """
    target_keys = set(keys) if keys is not None else set(env.keys())
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for k, v in env.items():
        if k in target_keys:
            redacted[k] = _redact_value(v, char=char, length=length, partial=partial)
            redacted_keys.append(k)
        else:
            redacted[k] = v

    return RedactResult(
        redacted=redacted,
        redacted_keys=redacted_keys,
        original_keys=list(env.keys()),
    )


def redact_string(
    env_string: str,
    keys: Optional[List[str]] = None,
    *,
    char: str = DEFAULT_REDACT_CHAR,
    length: int = DEFAULT_REDACT_LENGTH,
    partial: bool = False,
) -> RedactResult:
    """Parse *env_string* and redact the specified *keys*."""
    from envdiff.parser import parse_env_string

    env = parse_env_string(env_string)
    return redact_values(env, keys, char=char, length=length, partial=partial)
