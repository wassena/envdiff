"""Parser for .env files."""

import re
from typing import Dict, Optional, Tuple


COMMENT_RE = re.compile(r"^\s*#.*$")
BLANK_RE = re.compile(r"^\s*$")
KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def _strip_quotes(value: str) -> str:
    """Strip surrounding single or double quotes from a value."""
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_file(path: str) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comment lines (starting with #).
    - Strips surrounding quotes from values.
    - Raises ValueError on malformed lines.
    """
    result: Dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")
            if BLANK_RE.match(line) or COMMENT_RE.match(line):
                continue
            match = KEY_VALUE_RE.match(line)
            if not match:
                raise ValueError(
                    f"{path}:{lineno}: malformed line: {line!r}"
                )
            key, value = match.group(1), match.group(2).strip()
            result[key] = _strip_quotes(value)

    return result


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse .env content from a string (useful for testing)."""
    result: Dict[str, str] = {}

    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.rstrip()
        if BLANK_RE.match(line) or COMMENT_RE.match(line):
            continue
        match = KEY_VALUE_RE.match(line)
        if not match:
            raise ValueError(f"line {lineno}: malformed line: {line!r}")
        key, value = match.group(1), match.group(2).strip()
        result[key] = _strip_quotes(value)

    return result
