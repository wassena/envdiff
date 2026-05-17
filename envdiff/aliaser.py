"""aliaser.py – create aliased copies of env keys.

Given a mapping of {old_key: new_key}, each matched key is copied under
the new name.  The original key is kept by default (keep_original=True).
Keys not present in the mapping are passed through unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string


@dataclass
class AliasResult:
    values: Dict[str, str]
    aliased: List[str] = field(default_factory=list)   # new alias keys added
    skipped: List[str] = field(default_factory=list)   # requested but not found


def alias_count(result: AliasResult) -> int:
    return len(result.aliased)


def alias_values(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    keep_original: bool = True,
) -> AliasResult:
    """Return a new env dict with aliased keys applied.

    Args:
        env: source key/value pairs.
        mapping: {source_key: alias_key} pairs.
        keep_original: when False the source key is removed after aliasing.
    """
    result: Dict[str, str] = dict(env)
    aliased: List[str] = []
    skipped: List[str] = []

    for src, dst in mapping.items():
        if src not in env:
            skipped.append(src)
            continue
        result[dst] = env[src]
        aliased.append(dst)
        if not keep_original:
            result.pop(src, None)

    return AliasResult(values=result, aliased=aliased, skipped=skipped)


def alias_string(
    text: str,
    mapping: Dict[str, str],
    *,
    keep_original: bool = True,
) -> AliasResult:
    """Parse *text* as a .env string and apply aliasing."""
    env = parse_env_string(text)
    return alias_values(env, mapping, keep_original=keep_original)


def to_env_string(result: AliasResult) -> str:
    """Serialise result.values back to .env format."""
    return "".join(f"{k}={v}\n" for k, v in result.values.items())
