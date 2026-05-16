"""CLI entry-point for the *annotate* subcommand."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.annotator import annotate_string, annotated_count, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    kwargs = dict(
        prog="envdiff annotate",
        description="Attach inline comments to .env keys.",
    )
    parser = parent.add_parser("annotate", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("env_file", help="Path to the .env file to annotate.")
    parser.add_argument(
        "--set",
        dest="pairs",
        metavar="KEY=COMMENT",
        nargs="+",
        required=True,
        help="One or more KEY=COMMENT pairs.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Replace existing inline comments.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write result to FILE instead of stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    return parser


def _parse_pairs(pairs: list[str]) -> dict[str, str]:
    annotations: dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"Invalid KEY=COMMENT pair: {item!r}")
        key, _, comment = item.partition("=")
        annotations[key.strip()] = comment.strip()
    return annotations


def run(args: argparse.Namespace) -> int:
    source_path = Path(args.env_file)
    if not source_path.exists():
        print(f"error: file not found: {source_path}", file=sys.stderr)
        return 2

    try:
        annotations = _parse_pairs(args.pairs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    source = source_path.read_text()
    result = annotate_string(source, annotations, overwrite=args.overwrite)

    if args.format == "json":
        output = json.dumps({"values": result.values, "annotated": result.annotated}, indent=2)
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output, end="")

    return 0
