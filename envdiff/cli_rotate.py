"""CLI sub-command: envdiff rotate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.rotator import rotate_keys, to_env_string


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff rotate",
        description="Rename keys in an .env file according to a rotation map.",
    )
    parser = parent.add_parser("rotate", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("env_file", help="Source .env file")
    parser.add_argument(
        "--map",
        metavar="OLD=NEW",
        action="append",
        default=[],
        dest="mapping",
        help="Key rename rule (repeatable)",
    )
    parser.add_argument(
        "--map-file",
        metavar="FILE",
        help="JSON file mapping old key names to new key names",
    )
    parser.add_argument("--keep-old", action="store_true", help="Preserve original keys (marked deprecated)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write result to FILE instead of stdout")
    parser.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    return parser


def _build_rotation_map(args: argparse.Namespace) -> dict[str, str]:
    rotation_map: dict[str, str] = {}
    if args.map_file:
        data = json.loads(Path(args.map_file).read_text())
        rotation_map.update(data)
    for pair in args.mapping:
        if "=" not in pair:
            print(f"error: invalid --map value {pair!r} (expected OLD=NEW)", file=sys.stderr)
            sys.exit(2)
        old, new = pair.split("=", 1)
        rotation_map[old.strip()] = new.strip()
    return rotation_map


def run(args: argparse.Namespace) -> int:
    values = parse_env_file(args.env_file)
    rotation_map = _build_rotation_map(args)

    if not rotation_map:
        print("error: no rotation rules provided (use --map or --map-file)", file=sys.stderr)
        return 2

    result = rotate_keys(values, rotation_map, keep_old=args.keep_old)

    if args.format == "json":
        output = json.dumps({
            "values": result.values,
            "rotated": result.rotated,
            "skipped": result.skipped,
            "deprecated": result.deprecated,
        }, indent=2)
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output + "\n")
    else:
        print(output)

    return 0
