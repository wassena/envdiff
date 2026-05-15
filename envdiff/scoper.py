"""Scope filtering: keep or drop keys belonging to a named scope prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class ScopeResult:
    """Result of a scope operation."""

    kept: Dict[str, str] = field(default_factory=dict)
    dropped: Dict[str, str] = field(default_factory=dict)
    scope: str = ""
    strip_prefix: bool = True


def kept_count(result: ScopeResult) -> int:
    return len(result.kept)


def dropped_count(result: ScopeResult) -> int:
    return len(result.dropped)


def to_env_string(result: ScopeResult) -> str:
    lines = [f"{k}={v}" for k, v in result.kept.items()]
    return "\n".join(lines) + ("\n" if lines else "")


def scope_keys(
    env: Dict[str, str],
    scope: str,
    separator: str = "_",
    strip_prefix: bool = True,
    invert: bool = False,
) -> ScopeResult:
    """Keep only keys that belong to *scope* (i.e. start with ``scope + separator``).

    Parameters
    ----------
    env:          Parsed key/value mapping.
    scope:        Prefix to match (case-insensitive comparison is NOT performed).
    separator:    Character that separates the scope from the rest of the key.
    strip_prefix: When *True* the scope prefix (and separator) is removed from
                  the kept keys.
    invert:       When *True* the logic is reversed — keys that do NOT match the
                  scope are kept.
    """
    prefix = scope + separator
    result = ScopeResult(scope=scope, strip_prefix=strip_prefix)

    for key, value in env.items():
        matches = key.startswith(prefix)
        keep = matches if not invert else not matches

        if keep:
            out_key = key[len(prefix):] if (strip_prefix and matches) else key
            result.kept[out_key] = value
        else:
            result.dropped[key] = value

    return result


def scope_string(
    source: str,
    scope: str,
    separator: str = "_",
    strip_prefix: bool = True,
    invert: bool = False,
) -> ScopeResult:
    """Parse *source* then delegate to :func:`scope_keys`."""
    env = parse_env_string(source)
    return scope_keys(env, scope, separator=separator, strip_prefix=strip_prefix, invert=invert)
