"""Profile an .env file and produce summary statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class ProfileResult:
    total_keys: int
    empty_keys: List[str]
    duplicate_keys: List[str]  # detected from raw lines
    longest_key: str
    longest_value_key: str
    prefixes: Dict[str, int]  # prefix -> count
    values: Dict[str, str]

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    @property
    def prefix_count(self) -> int:
        return len(self.prefixes)


def _extract_prefix(key: str, separator: str = "_") -> str | None:
    idx = key.find(separator)
    return key[:idx] if idx > 0 else None


def _find_duplicates(raw: str) -> List[str]:
    seen: Dict[str, int] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            seen[key] = seen.get(key, 0) + 1
    return [k for k, count in seen.items() if count > 1]


def profile_string(raw: str, separator: str = "_") -> ProfileResult:
    values = parse_env_string(raw)
    duplicates = _find_duplicates(raw)

    empty_keys = [k for k, v in values.items() if v == ""]

    longest_key = max(values.keys(), key=len) if values else ""
    longest_value_key = max(values.keys(), key=lambda k: len(values[k])) if values else ""

    prefixes: Dict[str, int] = {}
    for key in values:
        prefix = _extract_prefix(key, separator)
        if prefix:
            prefixes[prefix] = prefixes.get(prefix, 0) + 1

    return ProfileResult(
        total_keys=len(values),
        empty_keys=empty_keys,
        duplicate_keys=duplicates,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        prefixes=prefixes,
        values=values,
    )


def profile_file(path: str, separator: str = "_") -> ProfileResult:
    raw = open(path, encoding="utf-8").read()
    return profile_string(raw, separator=separator)
