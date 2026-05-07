"""Generate .env.example files from existing .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file, parse_env_string


_REDACTED = "<REDACTED>"
_EMPTY = ""


@dataclass
class TemplateResult:
    keys: List[str] = field(default_factory=list)
    template: Dict[str, str] = field(default_factory=dict)

    def to_env_string(self) -> str:
        lines = []
        for key in self.keys:
            lines.append(f"{key}={self.template[key]}")
        return "\n".join(lines) + ("\n" if lines else "")


def build_template(
    env: Dict[str, str],
    *,
    redact: bool = True,
    keep_values: Optional[List[str]] = None,
    placeholder: str = _REDACTED,
) -> TemplateResult:
    """Return a TemplateResult where secret values are replaced.

    Args:
        env: Parsed key/value mapping.
        redact: When True, replace all values with *placeholder*.
        keep_values: Optional list of keys whose values should be kept as-is.
        placeholder: String used as the replacement value.
    """
    keep = set(keep_values or [])
    keys = list(env.keys())
    template: Dict[str, str] = {}
    for key in keys:
        if not redact or key in keep:
            template[key] = env[key]
        else:
            template[key] = placeholder
    return TemplateResult(keys=keys, template=template)


def template_from_file(
    path: str,
    *,
    redact: bool = True,
    keep_values: Optional[List[str]] = None,
    placeholder: str = _REDACTED,
) -> TemplateResult:
    """Parse *path* and build a template from it."""
    env = parse_env_file(path)
    return build_template(env, redact=redact, keep_values=keep_values, placeholder=placeholder)


def template_from_string(
    text: str,
    *,
    redact: bool = True,
    keep_values: Optional[List[str]] = None,
    placeholder: str = _REDACTED,
) -> TemplateResult:
    """Parse *text* and build a template from it."""
    env = parse_env_string(text)
    return build_template(env, redact=redact, keep_values=keep_values, placeholder=placeholder)
