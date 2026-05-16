"""CLI entry-point for the `envdiff split` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.splitter import split_string, write_split, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff split",
        description="Split a .env file into per-prefix files.",
    )
    parser = parent.add_parser("split", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Source .env file to split.")
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Directory to write split files into. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--separator", "-s",
        default="_",
        help="Key-prefix separator (default: '_').",
    )
    parser.add_argument(
        "--no-ungrouped",
        action="store_true",
        help="Drop keys that have no prefix group.",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format when writing to stdout.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    src = Path(args.file)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2

    result = split_string(
        src.read_text(),
        separator=args.separator,
        include_ungrouped=not args.no_ungrouped,
    )

    if args.output_dir:
        written = write_split(result, Path(args.output_dir))
        for p in written:
            print(f"wrote {p}")
        return 0

    # stdout mode
    if args.format == "json":
        payload = {prefix: env for prefix, env in result.files.items()}
        if result.ungrouped:
            payload["__ungrouped__"] = result.ungrouped
        print(json.dumps(payload, indent=2))
    else:
        for prefix, env in result.files.items():
            print(f"# --- {prefix} ---")
            print(to_env_string(env))
        if result.ungrouped:
            print("# --- ungrouped ---")
            print(to_env_string(result.ungrouped))

    return 0
