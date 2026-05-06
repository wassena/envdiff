"""CLI sub-command: reconcile two .env files."""

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs, has_differences
from envdiff.reconciler import reconcile, to_env_string


STRATEGIES = ("fill_missing", "overwrite", "prune_extra", "full_sync")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff reconcile",
        description="Reconcile a base .env file against a target.",
    )
    p.add_argument("base", help="Base .env file (will be updated).")
    p.add_argument("target", help="Target .env file to reconcile against.")
    p.add_argument(
        "--strategy",
        choices=STRATEGIES,
        default="fill_missing",
        help="Reconciliation strategy (default: fill_missing).",
    )
    p.add_argument(
        "--placeholder",
        default=None,
        metavar="VALUE",
        help="Use VALUE instead of the target value for new keys.",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write reconciled output to FILE (default: stdout).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing anything.",
    )
    return p


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_env = parse_env_file(args.base)
    target_env = parse_env_file(args.target)
    diff = diff_envs(base_env, target_env)

    if not has_differences(diff):
        print("No differences found — files are already in sync.", file=sys.stderr)
        return 0

    reconciled = reconcile(
        base_env,
        target_env,
        diff,
        strategy=args.strategy,
        placeholder=args.placeholder,
    )
    content = to_env_string(reconciled)

    if args.dry_run:
        print(content)
        return 0

    if args.output:
        Path(args.output).write_text(content)
        print(f"Reconciled output written to {args.output}", file=sys.stderr)
    else:
        print(content, end="")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
