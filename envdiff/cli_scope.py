"""CLI entry-point for the ``scope`` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.scoper import scope_keys, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    kwargs = dict(
        prog="envdiff scope",
        description="Keep or drop keys that belong to a named scope prefix.",
    )
    parser = parent.add_parser("scope", **kwargs) if parent else argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Path to the .env file.")
    parser.add_argument("scope", help="Scope prefix to filter on (e.g. DB).")
    parser.add_argument(
        "--separator", default="_", metavar="SEP",
        help="Separator between scope and key name (default: '_').",
    )
    parser.add_argument(
        "--no-strip", dest="strip_prefix", action="store_false",
        help="Keep the scope prefix in output key names.",
    )
    parser.add_argument(
        "--invert", action="store_true",
        help="Keep keys that do NOT match the scope.",
    )
    parser.add_argument(
        "--format", choices=["dotenv", "json"], default="dotenv",
        help="Output format (default: dotenv).",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE instead of stdout.")
    return parser


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(path))
    result = scope_keys(
        env,
        args.scope,
        separator=args.separator,
        strip_prefix=args.strip_prefix,
        invert=args.invert,
    )

    if args.format == "json":
        output = json.dumps(
            {
                "scope": result.scope,
                "kept": result.kept,
                "dropped": list(result.dropped.keys()),
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
