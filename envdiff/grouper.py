"""Group .env keys by prefix (e.g. DB_, AWS_, APP_) for organised display."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]  # prefix -> {key: value}
    ungrouped: Dict[str, str]          # keys with no recognised prefix

    def all_prefixes(self) -> List[str]:
        """Return sorted list of discovered prefixes."""
        return sorted(self.groups.keys())

    def total_keys(self) -> int:
        total = sum(len(v) for v in self.groups.values())
        return total + len(self.ungrouped)


def _extract_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment before *separator*, or None if none exists."""
    if separator not in key:
        return None
    prefix, _ = key.split(separator, 1)
    return prefix if prefix else None


def group_keys(
    env: Dict[str, str],
    *,
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Partition *env* into groups keyed by prefix.

    Keys whose prefix appears fewer than *min_group_size* times are placed in
    ``ungrouped``.
    """
    prefix_map: Dict[str, Dict[str, str]] = {}
    no_prefix: Dict[str, str] = {}

    for key, value in env.items():
        prefix = _extract_prefix(key, separator)
        if prefix is None:
            no_prefix[key] = value
        else:
            prefix_map.setdefault(prefix, {})[key] = value

    groups: Dict[str, Dict[str, str]] = {}
    for prefix, members in prefix_map.items():
        if len(members) >= min_group_size:
            groups[prefix] = members
        else:
            no_prefix.update(members)

    return GroupResult(groups=groups, ungrouped=no_prefix)


def group_from_string(
    text: str,
    *,
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Parse *text* as a .env string and group the resulting keys."""
    from envdiff.parser import parse_env_string

    env = parse_env_string(text)
    return group_keys(env, separator=separator, min_group_size=min_group_size)


def to_grouped_text(result: GroupResult) -> str:
    """Render a GroupResult as a human-readable string with section headers."""
    lines: List[str] = []
    for prefix in result.all_prefixes():
        lines.append(f"# [{prefix}]")
        for key, value in sorted(result.groups[prefix].items()):
            lines.append(f"{key}={value}")
        lines.append("")
    if result.ungrouped:
        lines.append("# [ungrouped]")
        for key, value in sorted(result.ungrouped.items()):
            lines.append(f"{key}={value}")
    return "\n".join(lines).rstrip()
