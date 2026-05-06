"""Validate .env files against a schema of required and optional keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Set


@dataclass
class ValidationResult:
    missing_required: Set[str] = field(default_factory=set)
    unknown_keys: Set[str] = field(default_factory=set)
    empty_values: Set[str] = field(default_factory=set)

    @property
    def is_valid(self) -> bool:
        return not (self.missing_required or self.unknown_keys or self.empty_values)

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            for key in sorted(self.missing_required):
                lines.append(f"  MISSING (required): {key}")
        if self.empty_values:
            for key in sorted(self.empty_values):
                lines.append(f"  EMPTY VALUE:        {key}")
        if self.unknown_keys:
            for key in sorted(self.unknown_keys):
                lines.append(f"  UNKNOWN KEY:        {key}")
        if not lines:
            return "All checks passed."
        return "\n".join(lines)


def validate(
    env: Dict[str, str],
    required: Iterable[str] = (),
    optional: Optional[Iterable[str]] = None,
    allow_empty: bool = False,
) -> ValidationResult:
    """Validate *env* dict against required/optional key lists.

    Args:
        env: Parsed environment mapping.
        required: Keys that must be present (and non-empty unless allow_empty).
        optional: When provided, any key not in required|optional is flagged as
                  unknown.  Pass ``None`` to skip unknown-key checking.
        allow_empty: When False, keys with empty string values are flagged.

    Returns:
        A :class:`ValidationResult` describing any violations found.
    """
    required_set: Set[str] = set(required)
    optional_set: Set[str] = set(optional) if optional is not None else set()
    known: Set[str] = required_set | optional_set

    result = ValidationResult()

    result.missing_required = required_set - env.keys()

    if not allow_empty:
        result.empty_values = {
            k for k, v in env.items() if k in required_set and v == ""
        }

    if optional is not None:
        result.unknown_keys = env.keys() - known

    return result
