"""CLI sub-command: envdiff snapshot — capture and compare env snapshots."""

from __future__ import annotations

import argparse
import sys

from envdiff.snapshot import create_snapshot, load_snapshot, save_snapshot, snapshot_values
from envdiff.differ import diff_envs, has_differences
from envdiff.formatter import render


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff snapshot",
        description="Capture or compare .env snapshots.",
    )
    sub = p.add_subparsers(dest="action", required=True)

    cap = sub.add_parser("capture", help="Save a snapshot of an env file.")
    cap.add_argument("env_file", help="Path to the .env file.")
    cap.add_argument("output", help="Path to write the .json snapshot.")
    cap.add_argument("--label", default=None, help="Human-readable label for the snapshot.")

    cmp = sub.add_parser("compare", help="Diff two snapshots (or a snapshot vs a live file).")
    cmp.add_argument("a", help="First snapshot (.json) or .env file.")
    cmp.add_argument("b", help="Second snapshot (.json) or .env file.")
    cmp.add_argument("--format", choices=["text", "json", "dotenv"], default="text")
    cmp.add_argument("--exit-code", action="store_true",
                     help="Exit 1 when differences exist.")
    return p


def _load_values(path: str) -> dict:
    if path.endswith(".json"):
        return snapshot_values(load_snapshot(path))
    from envdiff.parser import parse_env_file
    return parse_env_file(path)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.action == "capture":
        try:
            snap = create_snapshot(args.env_file, label=args.label)
            save_snapshot(snap, args.output)
            print(f"Snapshot saved to {args.output}  ({len(snap['values'])} keys)")
            return 0
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.action == "compare":
        try:
            a_vals = _load_values(args.a)
            b_vals = _load_values(args.b)
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        result = diff_envs(a_vals, b_vals)
        print(render(result, fmt=args.format))
        if args.exit_code and has_differences(result):
            return 1
        return 0

    return 0  # unreachable
