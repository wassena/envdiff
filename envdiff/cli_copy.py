"""CLI entry-point for the ``envdiff copy`` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.copier import copy_keys, to_env_string, copied_count
from envdiff.parser import parse_env_file


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Copy keys from SOURCE into TARGET and emit the merged result."
    if parent is not None:
        p = parent.add_parser("copy", help=description, description=description)
    else:
        p = argparse.ArgumentParser(prog="envdiff copy", description=description)

    p.add_argument("source", metavar="SOURCE", help="Source .env file")
    p.add_argument("target", metavar="TARGET", help="Target .env file")
    p.add_argument(
        "--keys", "-k",
        nargs="+",
        metavar="KEY",
        help="Keys to copy (default: all keys in SOURCE)",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Do not overwrite keys that already exist in TARGET",
    )
    p.add_argument(
        "--prefix",
        default="",
        metavar="PREFIX",
        help="Prepend PREFIX to each key written into TARGET",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    p.add_argument(
        "--format", "-f",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    return p


def run(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    target_path = Path(args.target)

    for p in (source_path, target_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    source = parse_env_file(str(source_path))
    target = parse_env_file(str(target_path))

    result = copy_keys(
        source,
        target,
        keys=args.keys,
        overwrite=not args.no_overwrite,
        prefix=args.prefix,
    )

    if args.format == "json":
        output = json.dumps(
            {
                "values": result.values,
                "copied": result.copied,
                "skipped": result.skipped,
                "copied_count": copied_count(result),
            },
            indent=2,
        )
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output, end="")

    return 0
