"""CLI entry-point for the `normalize` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.normalizer import normalize_string, normalized_count, to_env_string
from envdiff.parser import parse_env_file


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff normalize",
        description="Normalize keys and values in a .env file.",
    )
    parser = parent.add_parser("normalize", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Path to the .env file to normalize.")
    parser.add_argument("-o", "--output", help="Write result to this file instead of stdout.")
    parser.add_argument("--no-uppercase", action="store_true", help="Do not uppercase keys.")
    parser.add_argument("--no-trim", action="store_true", help="Do not trim value whitespace.")
    parser.add_argument("--no-bool", action="store_true", help="Do not normalize boolean values.")
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

    text = src.read_text()
    result = normalize_string(
        text,
        uppercase_keys=not args.no_uppercase,
        trim_values=not args.no_trim,
        normalize_bools=not args.no_bool,
    )

    if args.format == "json":
        output = json.dumps(
            {
                "values": result.values,
                "uppercased": result.uppercased,
                "trimmed": result.trimmed,
                "bool_normalized": result.bool_normalized,
                "normalized_count": normalized_count(result),
            },
            indent=2,
        )
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output + "\n")
    else:
        print(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    _parser = build_parser()
    sys.exit(run(_parser.parse_args()))
