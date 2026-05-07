"""Rename keys across a .env file or string."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class RenameResult:
    renamed: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    skipped: List[str] = field(default_factory=list)         # old keys not found
    env: Dict[str, str] = field(default_factory=dict)        # final key/value map

    @property
    def rename_count(self) -> int:
        return len(self.renamed)


def rename_keys(
    source: Dict[str, str],
    mapping: Dict[str, str],
    *,
    ignore_missing: bool = False,
) -> RenameResult:
    """Return a RenameResult after applying *mapping* (old -> new) to *source*.

    Parameters
    ----------
    source:
        Parsed key/value pairs from a .env file.
    mapping:
        Dict of {old_key: new_key} renames to apply.
    ignore_missing:
        When True, keys absent from *source* are silently skipped rather than
        recorded in ``result.skipped``.
    """
    result_env: Dict[str, str] = {}
    renamed: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in source.items():
        if key in mapping:
            new_key = mapping[key]
            result_env[new_key] = value
            renamed[key] = new_key
        else:
            result_env[key] = value

    for old_key in mapping:
        if old_key not in source:
            if not ignore_missing:
                skipped.append(old_key)

    return RenameResult(renamed=renamed, skipped=skipped, env=result_env)


def rename_in_string(
    env_string: str,
    mapping: Dict[str, str],
    *,
    ignore_missing: bool = False,
) -> RenameResult:
    """Parse *env_string* and apply renames, returning a RenameResult."""
    source = parse_env_string(env_string)
    return rename_keys(source, mapping, ignore_missing=ignore_missing)


def to_env_string(result: RenameResult) -> str:
    """Serialise the renamed env map back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in result.env.items()) + "\n"
