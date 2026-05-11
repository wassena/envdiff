"""CLI entry point for the extract sub-command.

Extracts a subset of keys from a .env file, optionally filling missing
keys with a default value and writing the result to a file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extractor import extract_from_string
from .formatter import format_dotenv


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    """Build (and optionally register) the argument parser for *extract*."""
    description = "Extract specific keys from a .env file."
    if parent is not None:
        parser = parent.add_parser("extract", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff extract", description=description)

    parser.add_argument(
        "env_file",
        metavar="ENV_FILE",
        help="Path to the source .env file.",
    )
    parser.add_argument(
        "keys",
        metavar="KEY",
        nargs="+",
        help="One or more keys to extract.",
    )
    parser.add_argument(
        "--default",
        metavar="VALUE",
        default=None,
        help="Value to use for keys that are absent in the source file.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["dotenv", "json"],
        default="dotenv",
        dest="fmt",
        help="Output format (default: dotenv).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any requested key is missing from the source.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the extract command; returns an exit code."""
    source = Path(args.env_file)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 2

    source_text = source.read_text(encoding="utf-8")
    result = extract_from_string(source_text, list(args.keys), default=args.default)

    if args.strict and result.missing_count > 0:
        missing = ", ".join(sorted(result.missing))
        print(f"error: missing keys: {missing}", file=sys.stderr)
        return 1

    # Render output
    if args.fmt == "json":
        output_text = json.dumps(result.values, indent=2)
    else:
        # Reuse the dotenv formatter for consistent output
        output_text = format_dotenv(result.values)

    if args.output:
        dest = Path(args.output)
        dest.write_text(output_text, encoding="utf-8")
    else:
        print(output_text, end="")

    return 0
