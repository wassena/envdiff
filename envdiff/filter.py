"""Filter keys from a parsed env mapping by pattern or explicit list."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class FilterResult:
    kept: Dict[str, str]
    removed: Dict[str, str]

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def filter_keys(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Return a FilterResult keeping or removing keys matched by *keys* / *patterns*.

    By default matched keys are **removed**.  Pass ``invert=True`` to keep only
    the matched keys (i.e. discard everything else).
    """
    if not keys and not patterns:
        return FilterResult(kept=dict(env), removed={})

    explicit: set = set(keys or [])
    compiled = _compile(patterns or [])

    def _matches(k: str) -> bool:
        if k in explicit:
            return True
        return any(rx.search(k) for rx in compiled)

    kept: Dict[str, str] = {}
    removed: Dict[str, str] = {}

    for k, v in env.items():
        matched = _matches(k)
        if invert:
            # keep only matched
            if matched:
                kept[k] = v
            else:
                removed[k] = v
        else:
            # remove matched
            if matched:
                removed[k] = v
            else:
                kept[k] = v

    return FilterResult(kept=kept, removed=removed)


def filter_string(
    source: str,
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Convenience wrapper that parses *source* before filtering."""
    env = parse_env_string(source)
    return filter_keys(env, keys=keys, patterns=patterns, invert=invert)


def filter_file(
    path: str,
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Convenience wrapper that reads *path* before filtering."""
    env = parse_env_file(path)
    return filter_keys(env, keys=keys, patterns=patterns, invert=invert)


def to_env_string(result: FilterResult) -> str:
    """Serialise the *kept* mapping back to .env format."""
    return "".join(f"{k}={v}\n" for k, v in result.kept.items())
