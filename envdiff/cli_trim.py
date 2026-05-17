"""CLI entry-point for the *trim* sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.trimmer import trim_values, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Strip whitespace from .env keys and/or values.")
    parser = (
        parent.add_parser("trim", **kwargs)
        if parent is not None
        else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("file", help="Input .env file.")
    parser.add_argument(
        "--trim-keys",
        action="store_true",
        default=False,
        help="Also strip whitespace from key names.",
    )
    parser.add_argument(
        "--no-trim-values",
        action="store_true",
        default=False,
        help="Do NOT strip whitespace from values.",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE.")
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = trim_values(
        env,
        trim_keys=args.trim_keys,
        trim_values=not args.no_trim_values,
    )

    if args.format == "json":
        text = json.dumps(
            {
                "values": result.values,
                "trimmed_keys": result.trimmed_keys,
                "trimmed_values": result.trimmed_values,
            },
            indent=2,
        )
    else:
        text = to_env_string(result)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    return 0
