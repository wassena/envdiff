"""CLI sub-command: strip — remove keys from a .env file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import parse_env_file
from .stripper import strip_keys, stripped_count, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Remove keys from a .env file by name or pattern.")
    parser = parent.add_parser("strip", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("env_file", help="Source .env file")
    parser.add_argument("-k", "--key", dest="keys", metavar="KEY", action="append", default=[], help="Key to strip (repeatable)")
    parser.add_argument("-p", "--pattern", dest="patterns", metavar="PATTERN", action="append", default=[], help="Regex pattern to match keys (repeatable)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE instead of stdout")
    parser.add_argument("--format", choices=["dotenv", "json"], default="dotenv", help="Output format (default: dotenv)")
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        values = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = strip_keys(values, keys=args.keys or None, patterns=args.patterns or None)

    if args.format == "json":
        output = json.dumps({"values": result.values, "stripped": result.stripped}, indent=2)
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(result.values)} keys ({stripped_count(result)} stripped) to {args.output}")
    else:
        sys.stdout.write(output)

    return 0
