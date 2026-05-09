"""Extract a subset of keys from a .env file or string."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_string


@dataclass
class ExtractResult:
    extracted: Dict[str, str]
    missing: List[str]
    source_keys: List[str]

    @property
    def found_count(self) -> int:
        return len(self.extracted)

    @property
    def missing_count(self) -> int:
        return len(self.missing)


def extract_keys(
    env: Dict[str, str],
    keys: List[str],
    default: Optional[str] = None,
) -> ExtractResult:
    """Return only the requested *keys* from *env*.

    Args:
        env: Parsed environment mapping.
        keys: Keys to extract.
        default: If given, use this value for keys absent from *env* instead
                 of recording them as missing.

    Returns:
        An :class:`ExtractResult` with the subset and any missing keys.
    """
    extracted: Dict[str, str] = {}
    missing: List[str] = []

    for key in keys:
        if key in env:
            extracted[key] = env[key]
        elif default is not None:
            extracted[key] = default
        else:
            missing.append(key)

    return ExtractResult(
        extracted=extracted,
        missing=missing,
        source_keys=list(env.keys()),
    )


def extract_from_string(
    text: str,
    keys: List[str],
    default: Optional[str] = None,
) -> ExtractResult:
    """Parse *text* as a .env string and extract *keys*."""
    env = parse_env_string(text)
    return extract_keys(env, keys, default=default)


def to_env_string(result: ExtractResult) -> str:
    """Serialise the extracted mapping back to .env format."""
    lines = [f"{k}={v}" for k, v in result.extracted.items()]
    return "\n".join(lines) + ("\n" if lines else "")
