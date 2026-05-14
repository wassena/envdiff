"""Inspect a .env file and report statistics and metadata about its contents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class InspectResult:
    total_keys: int
    empty_values: List[str]
    numeric_values: List[str]
    boolean_values: List[str]
    url_values: List[str]
    long_values: List[str]          # values > 80 chars
    prefixes: Dict[str, int]        # prefix -> count
    key_lengths: Dict[str, int]     # key -> len(value)

    @property
    def empty_count(self) -> int:
        return len(self.empty_values)

    @property
    def unique_prefixes(self) -> int:
        return len(self.prefixes)


def _detect_prefix(key: str, separator: str = "_") -> str | None:
    parts = key.split(separator, 1)
    return parts[0] if len(parts) > 1 else None


def inspect_values(env: Dict[str, str], separator: str = "_") -> InspectResult:
    """Analyse *env* dict and return an InspectResult with summary statistics."""
    empty: List[str] = []
    numeric: List[str] = []
    boolean: List[str] = []
    urls: List[str] = []
    long: List[str] = []
    prefixes: Dict[str, int] = {}
    lengths: Dict[str, int] = {}

    bool_values = {"true", "false", "yes", "no", "1", "0"}

    for key, value in env.items():
        lengths[key] = len(value)

        if value == "":
            empty.append(key)
        if value.lstrip("-").replace(".", "", 1).isdigit():
            numeric.append(key)
        if value.lower() in bool_values:
            boolean.append(key)
        if value.startswith(("http://", "https://", "ftp://")):
            urls.append(key)
        if len(value) > 80:
            long.append(key)

        prefix = _detect_prefix(key, separator)
        if prefix:
            prefixes[prefix] = prefixes.get(prefix, 0) + 1

    return InspectResult(
        total_keys=len(env),
        empty_values=empty,
        numeric_values=numeric,
        boolean_values=boolean,
        url_values=urls,
        long_values=long,
        prefixes=prefixes,
        key_lengths=lengths,
    )


def inspect_file(path: str, separator: str = "_") -> InspectResult:
    return inspect_values(parse_env_file(path), separator)


def inspect_string(text: str, separator: str = "_") -> InspectResult:
    return inspect_values(parse_env_string(text), separator)
