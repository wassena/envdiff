"""Lint .env files for common issues: duplicate keys, suspicious values, naming conventions."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line} [{self.code}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def by_code(self, code: str) -> List[LintIssue]:
        return [i for i in self.issues if i.code == code]


_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_SUSPICIOUS_RE = re.compile(r'(?i)(password|secret|token|key|api)')


def lint_lines(lines: List[str]) -> LintResult:
    """Lint raw lines from a .env file."""
    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if '=' not in stripped:
            result.issues.append(LintIssue(lineno, '', 'E001', 'Malformed line — no "=" found'))
            continue

        key, _, value = stripped.partition('=')
        key = key.strip()
        value = value.strip()

        # E002: duplicate key
        if key in seen_keys:
            result.issues.append(LintIssue(lineno, key, 'E002',
                f'Duplicate key (first seen on line {seen_keys[key]})'))
        else:
            seen_keys[key] = lineno

        # W001: key naming convention
        if not _KEY_RE.match(key):
            result.issues.append(LintIssue(lineno, key, 'W001',
                'Key should be UPPER_SNAKE_CASE starting with a letter'))

        # W002: sensitive key with empty value
        if _SUSPICIOUS_RE.search(key) and not value:
            result.issues.append(LintIssue(lineno, key, 'W002',
                'Sensitive key has an empty value'))

        # W003: value contains unquoted whitespace
        if value and not (value.startswith('"') or value.startswith("'")):
            if ' ' in value or '\t' in value:
                result.issues.append(LintIssue(lineno, key, 'W003',
                    'Value contains whitespace but is not quoted'))

    return result


def lint_file(path: str) -> LintResult:
    """Lint a .env file on disk."""
    with open(path, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    return lint_lines(lines)
