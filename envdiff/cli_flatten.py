"""CLI sub-command: envdiff flatten / expand."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.flattener import flatten_keys, expand_keys
from envdiff.parser import parse_env_file


def build_parser(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
    sub.add_argument("file", help=".env file to process")
    sub.add_argument(
        "--expand",
        action="store_true",
        help="Expand dotted keys to separator-delimited uppercase keys (reverse of flatten)",
    )
    sub.add_argument(
        "--separator",
        default="__",
        metavar="SEP",
        help="Separator used between key segments (default: __)",
    )
    sub.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    sub.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    return sub


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(path))
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.expand:
        result = expand_keys(env, separator=args.separator)
    else:
        result = flatten_keys(env, separator=args.separator)

    if args.format == "json":
        output = json.dumps(result.values, indent=2)
    else:
        lines = [f"{k}={v}" for k, v in result.values.items()]
        output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0
