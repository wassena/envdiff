"""Key rotation: rename keys according to a rotation map and track changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string


@dataclass
class RotateResult:
    values: Dict[str, str]
    rotated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    deprecated: List[str] = field(default_factory=list)


def rotated_count(result: RotateResult) -> int:
    return len(result.rotated)


def deprecated_count(result: RotateResult) -> int:
    return len(result.deprecated)


def rotate_keys(
    values: Dict[str, str],
    rotation_map: Dict[str, str],
    *,
    keep_old: bool = False,
) -> RotateResult:
    """Rename keys according to *rotation_map* (old_name -> new_name).

    If *keep_old* is True the original key is preserved alongside the new one
    and recorded in ``deprecated``.
    """
    result_values: Dict[str, str] = {}
    rotated: List[str] = []
    skipped: List[str] = []
    deprecated: List[str] = []

    old_to_new = rotation_map
    old_keys = set(old_to_new.keys())

    for key, value in values.items():
        if key in old_keys:
            new_key = old_to_new[key]
            result_values[new_key] = value
            rotated.append(key)
            if keep_old:
                result_values[key] = value
                deprecated.append(key)
        else:
            result_values[key] = value

    for old_key in old_keys:
        if old_key not in values:
            skipped.append(old_key)

    return RotateResult(
        values=result_values,
        rotated=rotated,
        skipped=skipped,
        deprecated=deprecated,
    )


def rotate_string(
    source: str,
    rotation_map: Dict[str, str],
    *,
    keep_old: bool = False,
) -> RotateResult:
    """Parse *source* as an .env string, apply rotation, return RotateResult."""
    values = parse_env_string(source)
    return rotate_keys(values, rotation_map, keep_old=keep_old)


def to_env_string(result: RotateResult) -> str:
    """Serialise the rotated values back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in result.values.items())
