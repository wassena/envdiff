"""CLI entry-point: envdiff patch — apply key=value patches to an env file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.patcher import patch_string, to_env_string


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff patch",
        description="Apply key=value patches to an env file.",
    )
    p.add_argument("file", help="Path to the .env file to patch.")
    p.add_argument(
        "patches",
        nargs="+",
        metavar="KEY=VALUE",
        help="One or more KEY=VALUE pairs to apply.",
    )
    p.add_argument("-o", "--output", help="Write result to this file (default: stdout).")
    p.add_argument(
        "--no-add",
        action="store_true",
        help="Do not add keys that are absent from the source file.",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of changes to stderr.",
    )
    return p


def _parse_patches(raw: List[str]) -> dict:
    patches: dict = {}
    for item in raw:
        if "=" not in item:
            print(f"error: invalid patch '{item}' — expected KEY=VALUE", file=sys.stderr)
            sys.exit(2)
        key, _, value = item.partition("=")
        patches[key.strip()] = value
    return patches


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source_path = Path(args.file)
    if not source_path.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    source = source_path.read_text(encoding="utf-8")
    patches = _parse_patches(args.patches)

    result = patch_string(source, patches, add_new=not args.no_add)

    if args.format == "json":
        output = json.dumps(result.env, indent=2)
    else:
        output = to_env_string(result)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")

    if args.summary:
        print(
            f"patch summary: {len(result.added)} added, "
            f"{len(result.updated)} updated, "
            f"{len(result.unchanged)} unchanged",
            file=sys.stderr,
        )

    return 0
