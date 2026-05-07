"""Sort keys in a .env file alphabetically or by a custom key order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envdiff.parser import parse_env_string


@dataclass
class SortResult:
    original_order: list[str]
    sorted_order: list[str]
    moved: list[str] = field(default_factory=list)

    @property
    def is_sorted(self) -> bool:
        return self.original_order == self.sorted_order


def sort_keys(
    env: dict[str, str],
    key_order: Optional[list[str]] = None,
    reverse: bool = False,
) -> SortResult:
    """Return a SortResult describing the reordering of *env* keys.

    Args:
        env: Parsed env mapping (preserves insertion order).
        key_order: Optional explicit ordering; keys not listed appear at the
                   end in alphabetical order.
        reverse: If True and *key_order* is None, sort Z→A.
    """
    original = list(env.keys())

    if key_order is not None:
        ordered = [k for k in key_order if k in env]
        remainder = sorted(k for k in env if k not in ordered)
        final = ordered + remainder
    else:
        final = sorted(original, reverse=reverse)

    moved = [k for k, f in zip(original, final) if k != f]
    return SortResult(original_order=original, sorted_order=final, moved=moved)


def to_sorted_env_string(
    env: dict[str, str],
    key_order: Optional[list[str]] = None,
    reverse: bool = False,
) -> str:
    """Render *env* as a .env string with keys in sorted order."""
    result = sort_keys(env, key_order=key_order, reverse=reverse)
    lines = [f"{k}={env[k]}" for k in result.sorted_order]
    return "\n".join(lines) + ("\n" if lines else "")


def sort_env_file(path: str, **kwargs) -> tuple[SortResult, str]:
    """Read *path*, sort it, and return (SortResult, new_content)."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    env = parse_env_string(raw)
    result = sort_keys(env, **kwargs)
    content = to_sorted_env_string(env, **kwargs)
    return result, content
