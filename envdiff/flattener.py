"""Flatten nested environment variable groups into a single dict, or expand
a flat dict back into prefixed keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class FlattenResult:
    values: Dict[str, str]
    expanded_keys: List[str] = field(default_factory=list)
    collapsed_keys: List[str] = field(default_factory=list)


def expanded_count(result: FlattenResult) -> int:
    return len(result.expanded_keys)


def collapsed_count(result: FlattenResult) -> int:
    return len(result.collapsed_keys)


def flatten_keys(
    env: Dict[str, str],
    separator: str = "__",
    prefix: Optional[str] = None,
) -> FlattenResult:
    """Collapse keys that share a common prefix into a dotted namespace.

    Keys such as ``DB__HOST`` and ``DB__PORT`` become ``db.host`` and
    ``db.port`` when *separator* is ``__``.
    """
    result: Dict[str, str] = {}
    collapsed: List[str] = []
    expanded: List[str] = []

    for key, value in env.items():
        if separator in key:
            parts = key.split(separator, 1)
            new_key = ".".join(p.lower() for p in parts)
            if prefix and not new_key.startswith(prefix.lower()):
                result[key] = value
                continue
            result[new_key] = value
            collapsed.append(key)
        else:
            result[key] = value
            expanded.append(key)

    return FlattenResult(values=result, expanded_keys=expanded, collapsed_keys=collapsed)


def expand_keys(
    env: Dict[str, str],
    separator: str = "__",
) -> FlattenResult:
    """Expand dotted keys back into separator-delimited uppercase keys.

    ``db.host`` becomes ``DB__HOST`` when *separator* is ``__``.
    """
    result: Dict[str, str] = {}
    expanded: List[str] = []
    collapsed: List[str] = []

    for key, value in env.items():
        if "." in key:
            new_key = separator.join(p.upper() for p in key.split("."))
            result[new_key] = value
            expanded.append(new_key)
        else:
            result[key] = value
            collapsed.append(key)

    return FlattenResult(values=result, expanded_keys=expanded, collapsed_keys=collapsed)


def flatten_string(source: str, separator: str = "__") -> FlattenResult:
    """Parse *source* as a .env string and flatten its keys."""
    return flatten_keys(parse_env_string(source), separator=separator)


def expand_string(source: str, separator: str = "__") -> FlattenResult:
    """Parse *source* as a .env string and expand its dotted keys."""
    return expand_keys(parse_env_string(source), separator=separator)
