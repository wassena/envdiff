"""Apply a set of key-value patches to an env file or string."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class PatchResult:
    env: Dict[str, str]
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)


def added_count(result: PatchResult) -> int:
    return len(result.added)


def updated_count(result: PatchResult) -> int:
    return len(result.updated)


def to_env_string(result: PatchResult) -> str:
    lines = [f"{k}={v}" for k, v in result.env.items()]
    return "\n".join(lines) + "\n" if lines else ""


def patch_values(
    env: Dict[str, str],
    patches: Dict[str, str],
    *,
    add_new: bool = True,
) -> PatchResult:
    """Apply *patches* onto *env*.

    Parameters
    ----------
    env:      base environment dictionary.
    patches:  key-value pairs to apply.
    add_new:  when False, keys absent from *env* are silently ignored.
    """
    result_env: Dict[str, str] = dict(env)
    added: List[str] = []
    updated: List[str] = []
    unchanged: List[str] = []

    for key, value in patches.items():
        if key not in result_env:
            if add_new:
                result_env[key] = value
                added.append(key)
        elif result_env[key] == value:
            unchanged.append(key)
        else:
            result_env[key] = value
            updated.append(key)

    return PatchResult(env=result_env, added=added, updated=updated, unchanged=unchanged)


def patch_string(
    source: str,
    patches: Dict[str, str],
    *,
    add_new: bool = True,
) -> PatchResult:
    """Parse *source* as an env string, apply *patches*, and return a PatchResult."""
    env = parse_env_string(source)
    return patch_values(env, patches, add_new=add_new)
