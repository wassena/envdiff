"""Encode .env values using base64 or url-safe encoding."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_string


@dataclass
class EncodeResult:
    values: Dict[str, str]
    encoded_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)


def encoded_count(result: EncodeResult) -> int:
    return len(result.encoded_keys)


def _encode_value(value: str, scheme: str) -> str:
    if scheme == "base64":
        return base64.b64encode(value.encode()).decode()
    if scheme == "urlenc":
        return urllib.parse.quote(value, safe="")
    raise ValueError(f"Unknown encoding scheme: {scheme!r}")


def encode_values(
    env: Dict[str, str],
    keys: List[str] | None = None,
    scheme: str = "base64",
    skip_already_encoded: bool = False,
) -> EncodeResult:
    """Encode selected (or all) values in *env* using *scheme*."""
    result_values: Dict[str, str] = {}
    encoded: List[str] = []
    skipped: List[str] = []

    target_keys = set(keys) if keys else set(env.keys())

    for k, v in env.items():
        if k not in target_keys:
            result_values[k] = v
            continue
        if skip_already_encoded and _looks_encoded(v, scheme):
            result_values[k] = v
            skipped.append(k)
            continue
        result_values[k] = _encode_value(v, scheme)
        encoded.append(k)

    return EncodeResult(values=result_values, encoded_keys=encoded, skipped_keys=skipped)


def encode_string(
    text: str,
    keys: List[str] | None = None,
    scheme: str = "base64",
    skip_already_encoded: bool = False,
) -> EncodeResult:
    env = parse_env_string(text)
    return encode_values(env, keys=keys, scheme=scheme, skip_already_encoded=skip_already_encoded)


def to_env_string(result: EncodeResult) -> str:
    return "\n".join(f"{k}={v}" for k, v in result.values.items())


def _looks_encoded(value: str, scheme: str) -> bool:
    if scheme == "base64":
        try:
            decoded = base64.b64decode(value, validate=True)
            return base64.b64encode(decoded).decode() == value
        except Exception:
            return False
    if scheme == "urlenc":
        return urllib.parse.unquote(value) != value
    return False
