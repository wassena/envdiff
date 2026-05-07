"""CLI entry-point for the `envdiff lint` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .linter import lint_file, LintResult


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Lint one or more .env files for common issues."
    if parent is not None:
        parser = parent.add_parser('lint', help=description)
    else:
        parser = argparse.ArgumentParser(prog='envdiff lint', description=description)

    parser.add_argument('files', nargs='+', metavar='FILE', help='.env file(s) to lint')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with code 1 on warnings as well as errors')
    return parser


def _format_text(path: str, result: LintResult) -> str:
    if result.ok:
        return f"{path}: OK\n"
    lines = [f"{path}:"]
    for issue in result.issues:
        lines.append(f"  {issue}")
    return '\n'.join(lines) + '\n'


def _format_json(results: dict[str, LintResult]) -> str:
    payload = {}
    for path, result in results.items():
        payload[path] = [
            {'line': i.line, 'key': i.key, 'code': i.code, 'message': i.message}
            for i in result.issues
        ]
    return json.dumps(payload, indent=2)


def run(args: argparse.Namespace) -> int:
    all_results: dict[str, LintResult] = {}
    exit_code = 0

    for path in args.files:
        try:
            result = lint_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2
        all_results[path] = result

        has_errors = any(i.code.startswith('E') for i in result.issues)
        has_warnings = any(i.code.startswith('W') for i in result.issues)
        if has_errors or (args.strict and has_warnings):
            exit_code = 1

    if args.format == 'json':
        print(_format_json(all_results))
    else:
        for path, result in all_results.items():
            print(_format_text(path, result), end='')

    return exit_code
