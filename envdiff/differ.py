"""Diff logic for comparing two parsed .env dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DiffResult:
    """Holds the categorised differences between two .env files."""

    # Keys present in source but missing in target
    missing_in_target: List[str] = field(default_factory=list)
    # Keys present in target but missing in source
    missing_in_source: List[str] = field(default_factory=list)
    # Keys present in both but with differing values
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (src_val, tgt_val)
    # Keys with identical values in both
    identical: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_target or self.missing_in_source or self.changed
        )


def diff_envs(
    source: Dict[str, str],
    target: Dict[str, str],
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        source: The reference environment (e.g. .env.example).
        target: The environment being checked (e.g. .env).

    Returns:
        A DiffResult describing all differences.
    """
    result = DiffResult()

    all_keys = set(source) | set(target)

    for key in sorted(all_keys):
        in_source = key in source
        in_target = key in target

        if in_source and not in_target:
            result.missing_in_target.append(key)
        elif in_target and not in_source:
            result.missing_in_source.append(key)
        elif source[key] != target[key]:
            result.changed[key] = (source[key], target[key])
        else:
            result.identical.append(key)

    return result
