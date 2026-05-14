"""CLI sub-command: envdiff inspect — show statistics for a .env file."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.inspector import inspect_file


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(description="Inspect a .env file and report statistics.")
    parser = (
        parent.add_parser("inspect", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("file", help="Path to .env file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--separator",
        default="_",
        help="Key prefix separator (default: _)",
    )
    return parser


def _format_text(result, path: str) -> str:
    lines = [
        f"File : {path}",
        f"Keys : {result.total_keys}",
        f"Empty values   : {result.empty_count}" + (
            f"  ({', '.join(result.empty_values)})" if result.empty_values else ""
        ),
        f"Numeric values : {len(result.numeric_values)}",
        f"Boolean values : {len(result.boolean_values)}",
        f"URL values     : {len(result.url_values)}",
        f"Long values    : {len(result.long_values)}",
        f"Unique prefixes: {result.unique_prefixes}",
    ]
    if result.prefixes:
        for prefix, count in sorted(result.prefixes.items()):
            lines.append(f"  {prefix}: {count} key(s)")
    return "\n".join(lines)


def _format_json(result, path: str) -> str:
    data = {
        "file": path,
        "total_keys": result.total_keys,
        "empty_values": result.empty_values,
        "numeric_values": result.numeric_values,
        "boolean_values": result.boolean_values,
        "url_values": result.url_values,
        "long_values": result.long_values,
        "prefixes": result.prefixes,
    }
    return json.dumps(data, indent=2)


def run(args: argparse.Namespace) -> int:
    try:
        result = inspect_file(args.file, separator=args.separator)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output = _format_json(result, args.file) if args.fmt == "json" else _format_text(result, args.file)
    print(output)
    return 0
