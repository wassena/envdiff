"""CLI sub-command: mask sensitive values in a .env file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.masker import DEFAULT_MASK, mask_string, to_masked_env_string


def build_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser("mask", help="Mask sensitive values in a .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--mask",
        default=DEFAULT_MASK,
        help="Replacement string for masked values (default: ***)",
    )
    p.add_argument(
        "--pattern",
        dest="patterns",
        action="append",
        metavar="REGEX",
        help="Key pattern to mask (repeatable); overrides defaults when provided",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Write result to this file instead of stdout",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.add_argument(
        "--list-masked",
        action="store_true",
        help="Print the names of masked keys to stderr",
    )
    return p


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    source = path.read_text()
    result = mask_string(source, patterns=args.patterns or None, mask=args.mask)

    if args.format == "json":
        output = json.dumps(result.masked, indent=2) + "\n"
    else:
        output = to_masked_env_string(result)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output, end="")

    if args.list_masked:
        for key in result.masked_keys:
            print(f"masked: {key}", file=sys.stderr)

    return 0
