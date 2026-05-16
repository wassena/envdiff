"""CLI entry-point for the ``envdiff freeze`` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.freezer import freeze_string, freeze_values, frozen_count


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff freeze",
        description="Append frozen markers to keys in an .env file.",
    )
    parser = parent.add_parser("freeze", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Input .env file")
    parser.add_argument("-k", "--key", dest="keys", metavar="KEY", action="append",
                        help="Key(s) to freeze (repeatable); omit to freeze all")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="Write result to FILE instead of stdout")
    parser.add_argument("--format", choices=["dotenv", "json"], default="dotenv",
                        help="Output format (default: dotenv)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be frozen without writing")
    return parser


def run(args: argparse.Namespace) -> int:
    src = Path(args.file)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2

    env_string = src.read_text(encoding="utf-8")
    keys: list[str] | None = args.keys or None

    result = freeze_values(env_string, keys=keys)

    if args.format == "json":
        payload = {
            "values": result.values,
            "frozen": result.frozen_keys,
            "already_frozen": result.already_frozen,
            "frozen_count": frozen_count(result),
        }
        output = json.dumps(payload, indent=2)
    else:
        output = freeze_string(env_string, keys=keys)

    if args.dry_run or not args.output:
        print(output)
    else:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Froze {frozen_count(result)} key(s) → {args.output}")

    return 0
