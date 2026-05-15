"""CLI entry-point for the ``envdiff pin`` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.pinner import pin_string, pinned_count, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(
        prog="envdiff pin",
        description="Pin one or more keys to fixed values in a .env file.",
    )
    parser = parent.add_parser("pin", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("env_file", help="Path to the .env file to process.")
    parser.add_argument(
        "--set",
        metavar="KEY=VALUE",
        dest="pins",
        action="append",
        default=[],
        required=True,
        help="Key=value pair to pin (repeatable).",
    )
    parser.add_argument(
        "--no-add",
        action="store_true",
        default=False,
        help="Do not add keys that are absent from the source file.",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE instead of stdout.")
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    return parser


def _parse_pins(raw: list[str]) -> dict[str, str]:
    pins: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid KEY=VALUE pair: {item!r}")
        key, _, value = item.partition("=")
        pins[key.strip()] = value
    return pins


def run(args: argparse.Namespace) -> int:
    source = Path(args.env_file).read_text()
    try:
        pins = _parse_pins(args.pins)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = pin_string(source, pins, add_missing=not args.no_add)

    if args.format == "json":
        output = json.dumps(
            {
                "values": result.values,
                "pinned": result.pinned,
                "skipped": result.skipped,
                "pinned_count": pinned_count(result),
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
