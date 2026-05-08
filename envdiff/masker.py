"""Mask sensitive values in .env files based on key patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string

DEFAULT_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

DEFAULT_MASK = "***"


@dataclass
class MaskResult:
    masked: Dict[str, str]
    masked_keys: List[str]
    original_keys: List[str]

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def mask_values(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> MaskResult:
    """Return a copy of env with sensitive values replaced by mask."""
    compiled = _compile_patterns(patterns or DEFAULT_PATTERNS)
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if any(p.fullmatch(key) for p in compiled):
            masked[key] = mask
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(
        masked=masked,
        masked_keys=sorted(masked_keys),
        original_keys=list(env.keys()),
    )


def mask_string(
    source: str,
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> MaskResult:
    """Parse an env string and mask sensitive values."""
    env = parse_env_string(source)
    return mask_values(env, patterns=patterns, mask=mask)


def to_masked_env_string(result: MaskResult) -> str:
    """Serialise a MaskResult back to .env format."""
    lines = [f"{k}={v}" for k, v in result.masked.items()]
    return "\n".join(lines) + ("\n" if lines else "")
