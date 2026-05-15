"""Deduplicator: remove duplicate keys from a .env file, keeping the last occurrence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_string


@dataclass
class DedupeResult:
    """Result of a deduplication pass."""

    env: Dict[str, str]
    duplicates: List[str] = field(default_factory=list)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)


def _iter_pairs(text: str) -> List[Tuple[str, str]]:
    """Return all (key, value) pairs in order, including duplicates."""
    pairs: List[Tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key:
            pairs.append((key, value.strip()))
    return pairs


def deduplicate(text: str, keep: str = "last") -> DedupeResult:
    """Remove duplicate keys from *text*.

    Parameters
    ----------
    text:
        Raw .env content.
    keep:
        ``"last"`` (default) keeps the final definition; ``"first"`` keeps the
        first definition.

    Returns
    -------
    DedupeResult
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    pairs = _iter_pairs(text)
    seen: Dict[str, int] = {}
    for idx, (key, _) in enumerate(pairs):
        seen[key] = seen.get(key, 0) + 1

    duplicates = sorted(k for k, count in seen.items() if count > 1)

    # Build deduplicated mapping
    if keep == "last":
        env: Dict[str, str] = {}
        for key, value in pairs:
            env[key] = value  # later values overwrite earlier ones
    else:
        env = {}
        for key, value in pairs:
            if key not in env:
                env[key] = value

    return DedupeResult(env=env, duplicates=duplicates)


def to_env_string(result: DedupeResult) -> str:
    """Serialise a DedupeResult back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in result.env.items()) + "\n"


def deduplicate_file(path: str, keep: str = "last", write: bool = False) -> DedupeResult:
    """Deduplicate a .env file on disk.

    Parameters
    ----------
    path:
        Path to the .env file to process.
    keep:
        ``"last"`` (default) or ``"first"`` — which occurrence to retain.
    write:
        If ``True``, overwrite *path* with the deduplicated content.

    Returns
    -------
    DedupeResult
    """
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    result = deduplicate(text, keep=keep)

    if write and result.has_duplicates:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(to_env_string(result))

    return result
