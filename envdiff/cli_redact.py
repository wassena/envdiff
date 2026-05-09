"""CLI sub-command: redact — redact sensitive values in a .env file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.redactor import redact_values
from envdiff.parser import parse_env_file


def build_parser(parent: "argparse._SubParsersAction | None" = None) -> argparse.ArgumentParser:  # noqa: F821
    kwargs = dict(
        prog="envdiff redact",
        description="Redact sensitive values in a .env file.",
    )
    parser = parent.add_parser("redact", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--keys", "-k",
        nargs="+",
        metavar="KEY",
        help="Keys to redact (default: all keys)",
    )
    parser.add_argument(
        "--char", "-c",
        default="*",
        help="Character used for redaction (default: *)",
    )
    parser.add_argument(
        "--length", "-l",
        type=int,
        default=8,
        help="Length of the redaction string (default: 8)",
    )
    parser.add_argument(
        "--partial",
        action="store_true",
        help="Keep first/last two characters of the value",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["dotenv", "json"],
        default="dotenv",
        dest="fmt",
        help="Output format (default: dotenv)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    env = parse_env_file(path)
    result = redact_values(
        env,
        args.keys,
        char=args.char,
        length=args.length,
        partial=args.partial,
    )

    if args.fmt == "json":
        output = json.dumps(result.redacted, indent=2)
    else:
        lines = [f"{k}={v}" for k, v in result.redacted.items()]
        output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0
