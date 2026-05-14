"""Promote values from one environment to another, with optional key filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse_env_file, parse_env_string


@dataclass
class PromoteResult:
    promoted: Dict[str, str]          # keys copied from source to target
    skipped: List[str]                # keys not promoted (not in source or filtered out)
    overwritten: List[str]            # keys that already existed in target and were replaced
    base: Dict[str, str]              # original target env


def promoted_count(result: PromoteResult) -> int:
    return len(result.promoted)


def overwrite_count(result: PromoteResult) -> int:
    return len(result.overwritten)


def to_env_string(result: PromoteResult) -> str:
    """Render the merged target env (base updated with promoted values) as a .env string."""
    merged = {**result.base, **result.promoted}
    return "\n".join(f"{k}={v}" for k, v in merged.items()) + "\n"


def promote(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> PromoteResult:
    """Promote values from *source* into *target*.

    Args:
        source:    The authoritative environment to pull values from.
        target:    The environment being updated.
        keys:      If given, only these keys are considered for promotion.
                   Keys absent from *source* are recorded in ``skipped``.
        overwrite: When False, keys already present in *target* are left
                   unchanged and recorded in ``skipped`` instead.
    """
    candidates = keys if keys is not None else list(source.keys())

    promoted: Dict[str, str] = {}
    skipped: List[str] = []
    overwritten: List[str] = []

    for key in candidates:
        if key not in source:
            skipped.append(key)
            continue
        if key in target and not overwrite:
            skipped.append(key)
            continue
        if key in target:
            overwritten.append(key)
        promoted[key] = source[key]

    return PromoteResult(
        promoted=promoted,
        skipped=skipped,
        overwritten=overwritten,
        base=dict(target),
    )


def promote_files(
    source_path: str,
    target_path: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> PromoteResult:
    source = parse_env_file(source_path)
    target = parse_env_file(target_path)
    return promote(source, target, keys=keys, overwrite=overwrite)


def promote_strings(
    source_text: str,
    target_text: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> PromoteResult:
    source = parse_env_string(source_text)
    target = parse_env_string(target_text)
    return promote(source, target, keys=keys, overwrite=overwrite)
