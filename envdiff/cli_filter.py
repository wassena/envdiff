"""CLI sub-command: envdiff filter

Remove (or keep) keys from a .env file by explicit name or regex pattern.

Examples
--------
  envdiff filter .env --keys SECRET TOKEN          # drop those keys
  envdiff filter .env --pattern '^TEST_'           # drop keys matching regex
  envdiff filter .env --keys DEBUG --invert        # keep ONLY DEBUG
  envdiff filter .env --pattern '_KEY$' --invert   # keep only *_KEY keys
"""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.filter import filter_file, to_env_string


def build_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff filter",
        description="Remove or keep keys from a .env file.",
    )
    parser = (
        parent.add_parser("filter", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--keys", nargs="+", metavar="KEY", default=[], help="Explicit key names to match"
    )
    parser.add_argument(
        "--pattern",
        nargs="+",
        metavar="REGEX",
        default=[],
        help="Regex patterns to match key names",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Keep matched keys instead of removing them",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE")
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        result = filter_file(
            args.env_file,
            keys=args.keys or None,
            patterns=args.pattern or None,
            invert=args.invert,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        text = json.dumps({"kept": result.kept, "removed": result.removed}, indent=2)
    else:
        text = to_env_string(result)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(text)
    else:
        print(text, end="")

    return 0
