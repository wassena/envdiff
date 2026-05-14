"""CLI sub-command: envdiff cast

Infer and display native Python types for values in a .env file.
"""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.caster import cast_file, cast_count, summary


def build_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Infer native types (bool/int/float) for .env values."
    if subparsers is not None:
        parser = subparsers.add_parser("cast", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff cast", description=description)

    parser.add_argument("env_file", help="Path to the .env file to analyse.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--non-string-only",
        action="store_true",
        help="Only report keys whose value is not a plain string.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        result = cast_file(args.env_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {
            "source": result.source,
            "cast_count": cast_count(result),
            "values": {
                k: {"value": v, "type": result.casts[k]}
                for k, v in result.values.items()
                if not args.non_string_only or result.casts[k] != "str"
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        items = (
            [(k, result.values[k], result.casts[k]) for k in result.values
             if result.casts[k] != "str"]
            if args.non_string_only
            else [(k, result.values[k], result.casts[k]) for k in result.values]
        )
        if not items:
            print("No non-string values detected.")
        else:
            for key, val, typename in items:
                print(f"{key}={val!r}  # {typename}")

    return 0


if __name__ == "__main__":
    _parser = build_parser()
    sys.exit(run(_parser.parse_args()))
