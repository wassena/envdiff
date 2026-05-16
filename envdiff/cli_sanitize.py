"""CLI entry-point for the *sanitize* sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.sanitizer import sanitize_string, sanitized_count, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff sanitize",
        description="Strip control characters and unsafe whitespace from .env values.",
    )
    parser = parent.add_parser("sanitize", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Path to the .env file to sanitize.")
    parser.add_argument("-o", "--output", help="Write result to this file (default: stdout).")
    parser.add_argument(
        "--no-strip-whitespace",
        action="store_true",
        default=False,
        help="Do not strip leading/trailing whitespace from values.",
    )
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    src = Path(args.file)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2

    text = src.read_text(encoding="utf-8")
    result = sanitize_string(text, strip_whitespace=not args.no_strip_whitespace)

    if args.format == "json":
        output = json.dumps(
            {
                "values": result.values,
                "sanitized": result.sanitized,
                "sanitized_count": sanitized_count(result),
            },
            indent=2,
        )
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")

    return 0
