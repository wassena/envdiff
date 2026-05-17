"""Copy specific keys from one env mapping to another."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class CopyResult:
    values: Dict[str, str]
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    comments: Dict[str, str] = field(default_factory=dict)


def copied_count(result: CopyResult) -> int:
    return len(result.copied)


def copy_keys(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    *,
    overwrite: bool = True,
    prefix: str = "",
) -> CopyResult:
    """Copy keys from *source* into *target*.

    Args:
        source:    Source env mapping.
        target:    Target env mapping (not mutated; a copy is returned).
        keys:      Explicit list of keys to copy.  ``None`` copies all keys.
        overwrite: When *False*, existing keys in target are left unchanged.
        prefix:    Optional prefix prepended to each key in the target.
    """
    result_values = dict(target)
    copied: List[str] = []
    skipped: List[str] = []

    candidates = keys if keys is not None else list(source.keys())

    for key in candidates:
        if key not in source:
            skipped.append(key)
            continue

        dest_key = f"{prefix}{key}" if prefix else key

        if dest_key in result_values and not overwrite:
            skipped.append(key)
            continue

        result_values[dest_key] = source[key]
        copied.append(key)

    return CopyResult(values=result_values, copied=copied, skipped=skipped)


def copy_string(
    source_str: str,
    target_str: str,
    keys: Optional[List[str]] = None,
    *,
    overwrite: bool = True,
    prefix: str = "",
) -> CopyResult:
    """Parse both strings and delegate to :func:`copy_keys`."""
    source = parse_env_string(source_str)
    target = parse_env_string(target_str)
    return copy_keys(source, target, keys, overwrite=overwrite, prefix=prefix)


def to_env_string(result: CopyResult) -> str:
    """Serialise *result.values* back to .env format."""
    return "".join(f"{k}={v}\n" for k, v in result.values.items())
