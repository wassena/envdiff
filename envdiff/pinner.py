"""Pin specific env keys to fixed values, recording what was changed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string


@dataclass
class PinResult:
    values: Dict[str, str]
    pinned: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def pinned_count(result: PinResult) -> int:
    """Return the number of keys that were pinned."""
    return len(result.pinned)


def pin_values(
    env: Dict[str, str],
    pins: Dict[str, str],
    *,
    add_missing: bool = True,
) -> PinResult:
    """Pin keys in *env* to the values supplied in *pins*.

    Parameters
    ----------
    env:
        Source environment mapping.
    pins:
        Mapping of key -> desired fixed value.
    add_missing:
        When ``True`` (default), keys present in *pins* but absent from *env*
        are added.  When ``False`` those keys are recorded in ``skipped``.
    """
    result = dict(env)
    pinned: List[str] = []
    skipped: List[str] = []

    for key, value in pins.items():
        if key not in result and not add_missing:
            skipped.append(key)
            continue
        if result.get(key) != value:
            result[key] = value
            pinned.append(key)

    return PinResult(values=result, pinned=pinned, skipped=skipped)


def pin_string(
    source: str,
    pins: Dict[str, str],
    *,
    add_missing: bool = True,
) -> PinResult:
    """Parse *source* as a .env string, apply pins, and return a PinResult."""
    env = parse_env_string(source)
    return pin_values(env, pins, add_missing=add_missing)


def to_env_string(result: PinResult) -> str:
    """Serialise the result values back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in result.values.items())
