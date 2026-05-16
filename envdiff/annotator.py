"""Annotate .env keys with inline comments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envdiff.parser import parse_env_string


@dataclass
class AnnotateResult:
    values: Dict[str, str]
    annotations: Dict[str, str]
    annotated: list[str] = field(default_factory=list)


def annotated_count(result: AnnotateResult) -> int:
    return len(result.annotated)


def annotate_values(
    env: Dict[str, str],
    annotations: Dict[str, str],
    overwrite: bool = False,
) -> AnnotateResult:
    """Attach inline comments to matching keys.

    Args:
        env: Parsed key/value mapping.
        annotations: Mapping of key -> comment text (without leading ``#``).
        overwrite: If *True*, replace existing inline comments.

    Returns:
        AnnotateResult with updated values and metadata.
    """
    annotated: list[str] = []
    result: Dict[str, str] = dict(env)

    for key, comment in annotations.items():
        if key not in result:
            continue
        value = result[key]
        # Strip any existing inline comment before re-annotating.
        if "  #" in value:
            if not overwrite:
                continue
            value = value[: value.index("  #")].rstrip()
        result[key] = f"{value}  # {comment}"
        annotated.append(key)

    return AnnotateResult(values=result, annotations=annotations, annotated=annotated)


def annotate_string(
    source: str,
    annotations: Dict[str, str],
    overwrite: bool = False,
) -> AnnotateResult:
    """Parse *source* then annotate."""
    env = parse_env_string(source)
    return annotate_values(env, annotations, overwrite=overwrite)


def to_env_string(result: AnnotateResult) -> str:
    """Serialise annotated values back to .env format."""
    lines = []
    for key, value in result.values.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
