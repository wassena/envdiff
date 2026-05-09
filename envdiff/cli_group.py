"""CLI sub-command: envdiff group — display .env keys organised by prefix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.grouper import group_keys, to_grouped_text
from envdiff.parser import parse_env_file


def build_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "group",
        help="Group .env keys by prefix for organised display.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Prefix separator character (default: '_').",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        metavar="N",
        help="Minimum keys sharing a prefix to form a group (default: 1).",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return p


def run(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = group_keys(
        env,
        separator=args.separator,
        min_group_size=args.min_group_size,
    )

    if args.format == "json":
        payload = {
            "groups": {p: dict(sorted(v.items())) for p, v in sorted(result.groups.items())},
            "ungrouped": dict(sorted(result.ungrouped.items())),
            "total_keys": result.total_keys(),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(to_grouped_text(result))

    return 0
