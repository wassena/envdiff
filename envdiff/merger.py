"""Merge multiple .env files into a single combined result.

Later files take precedence over earlier ones (last-write-wins).
Optionally report which keys were overridden during the merge.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class MergeResult:
    """Outcome of merging two or more env sources."""

    merged: Dict[str, str]
    # key -> list of (source_index, value) pairs that were overridden
    overrides: Dict[str, List[Tuple[int, str]]] = field(default_factory=dict)

    @property
    def override_count(self) -> int:
        return len(self.overrides)


def merge_files(*paths: str) -> MergeResult:
    """Merge env files from *paths*. Later paths win on conflict.

    Args:
        *paths: One or more file-system paths to .env files.

    Returns:
        A :class:`MergeResult` describing the merged mapping and any
        keys that were overridden by a later source.

    Raises:
        FileNotFoundError: If any of the supplied paths does not exist.
        ValueError: If fewer than two paths are provided.
    """
    if len(paths) < 2:
        raise ValueError("merge_files requires at least two file paths.")

    sources: List[Dict[str, str]] = [parse_env_file(p) for p in paths]
    return _merge(sources)


def merge_strings(*env_strings: str) -> MergeResult:
    """Merge env content supplied as raw strings. Later strings win.

    Args:
        *env_strings: Two or more raw .env-formatted strings.

    Returns:
        A :class:`MergeResult` with the combined mapping.

    Raises:
        ValueError: If fewer than two strings are provided.
    """
    if len(env_strings) < 2:
        raise ValueError("merge_strings requires at least two env strings.")

    sources: List[Dict[str, str]] = [parse_env_string(s) for s in env_strings]
    return _merge(sources)


def _merge(sources: List[Dict[str, str]]) -> MergeResult:
    merged: Dict[str, str] = {}
    overrides: Dict[str, List[Tuple[int, str]]] = {}

    for idx, source in enumerate(sources):
        for key, value in source.items():
            if key in merged:
                overrides.setdefault(key, [])
                # record the value that is being displaced
                overrides[key].append((idx - 1, merged[key]))
            merged[key] = value

    return MergeResult(merged=merged, overrides=overrides)
