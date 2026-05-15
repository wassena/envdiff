"""Compare two .env files or strings and produce a structured comparison report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class CompareResult:
    """Structured result of comparing two env sources."""

    source_a: str
    source_b: str
    common: Dict[str, str] = field(default_factory=dict)
    only_in_a: Dict[str, str] = field(default_factory=dict)
    only_in_b: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)


def total_keys(result: CompareResult) -> int:
    """Total unique keys across both sources."""
    return len(set(result.common) | set(result.only_in_a) | set(result.only_in_b) | set(result.changed))


def similarity_score(result: CompareResult) -> float:
    """Return a 0.0–1.0 score representing how similar the two sources are."""
    total = total_keys(result)
    if total == 0:
        return 1.0
    matching = len(result.common)
    return round(matching / total, 4)


def _compare(a: Dict[str, str], b: Dict[str, str], label_a: str, label_b: str) -> CompareResult:
    result = CompareResult(source_a=label_a, source_b=label_b)
    all_keys = set(a) | set(b)
    for key in all_keys:
        in_a = key in a
        in_b = key in b
        if in_a and in_b:
            if a[key] == b[key]:
                result.common[key] = a[key]
            else:
                result.changed[key] = (a[key], b[key])
        elif in_a:
            result.only_in_a[key] = a[key]
        else:
            result.only_in_b[key] = b[key]
    return result


def compare_files(path_a: str, path_b: str) -> CompareResult:
    """Compare two .env files and return a CompareResult."""
    return _compare(parse_env_file(path_a), parse_env_file(path_b), path_a, path_b)


def compare_strings(text_a: str, text_b: str, label_a: str = "A", label_b: str = "B") -> CompareResult:
    """Compare two .env strings and return a CompareResult."""
    return _compare(parse_env_string(text_a), parse_env_string(text_b), label_a, label_b)
