"""Split a single .env file into multiple files by prefix group."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string
from envdiff.grouper import group_keys


@dataclass
class SplitResult:
    files: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.files.values()) + len(self.ungrouped)


def to_env_string(env: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in env.items()) + "\n" if env else ""


def split_by_prefix(
    env: Dict[str, str],
    separator: str = "_",
    include_ungrouped: bool = True,
) -> SplitResult:
    """Split *env* dict into per-prefix buckets."""
    grouped = group_keys(env, separator=separator)
    result = SplitResult()

    for prefix in grouped.all_prefixes:
        result.files[prefix] = grouped.get_group(prefix)

    if include_ungrouped and grouped.ungrouped:
        result.ungrouped = dict(grouped.ungrouped)

    return result


def split_string(
    source: str,
    separator: str = "_",
    include_ungrouped: bool = True,
) -> SplitResult:
    env = parse_env_string(source)
    return split_by_prefix(env, separator=separator, include_ungrouped=include_ungrouped)


def write_split(
    result: SplitResult,
    output_dir: Path,
    ungrouped_filename: str = "ungrouped.env",
) -> List[Path]:
    """Write each bucket to *output_dir*/<PREFIX>.env; return written paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    for prefix, env in result.files.items():
        path = output_dir / f"{prefix.lower()}.env"
        path.write_text(to_env_string(env))
        written.append(path)

    if result.ungrouped:
        path = output_dir / ungrouped_filename
        path.write_text(to_env_string(result.ungrouped))
        written.append(path)

    return written
