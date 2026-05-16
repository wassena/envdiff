"""Strip keys from .env content based on a list or pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse_env_string


@dataclass
class StripResult:
    values: Dict[str, str]
    stripped: List[str] = field(default_factory=list)


def stripped_count(result: StripResult) -> int:
    return len(result.stripped)


def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def strip_keys(
    values: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> StripResult:
    """Remove keys from *values* that match any of *keys* or *patterns*."""
    keys_set = set(keys or [])
    compiled = _compile(patterns or [])
    result: Dict[str, str] = {}
    stripped: List[str] = []

    for k, v in values.items():
        matched = k in keys_set or any(p.search(k) for p in compiled)
        if matched:
            stripped.append(k)
        else:
            result[k] = v

    return StripResult(values=result, stripped=sorted(stripped))


def strip_string(
    env_string: str,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> StripResult:
    """Parse *env_string* and strip matching keys."""
    values = parse_env_string(env_string)
    return strip_keys(values, keys=keys, patterns=patterns)


def to_env_string(result: StripResult) -> str:
    """Serialise a StripResult back to .env format."""
    return "".join(f"{k}={v}\n" for k, v in result.values.items())
