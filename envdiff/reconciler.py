"""Reconcile two .env files by merging or patching differences."""

from typing import Dict, Optional
from envdiff.differ import DiffResult


def reconcile(
    base: Dict[str, str],
    target: Dict[str, str],
    diff: DiffResult,
    strategy: str = "fill_missing",
    placeholder: Optional[str] = None,
) -> Dict[str, str]:
    """
    Reconcile *base* against *target* using the given strategy.

    Strategies
    ----------
    fill_missing   : copy keys missing in base from target (or placeholder).
    overwrite      : apply all target values onto base (adds + updates).
    prune_extra    : remove keys in base that are absent in target.
    full_sync      : fill_missing + overwrite + prune_extra combined.
    """
    if strategy not in ("fill_missing", "overwrite", "prune_extra", "full_sync"):
        raise ValueError(f"Unknown reconcile strategy: {strategy!r}")

    result = dict(base)

    if strategy in ("fill_missing", "full_sync"):
        for key in diff.missing_in_a:
            result[key] = placeholder if placeholder is not None else target[key]

    if strategy in ("overwrite", "full_sync"):
        for key in diff.changed:
            result[key] = target[key]

    if strategy in ("prune_extra", "full_sync"):
        for key in diff.missing_in_b:
            result.pop(key, None)

    return result


def to_env_string(env: Dict[str, str]) -> str:
    """Serialize a key/value mapping back to .env file content."""
    lines = []
    for key, value in env.items():
        # Quote values that contain spaces or are empty
        if " " in value or value == "":
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
