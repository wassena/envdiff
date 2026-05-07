"""Entry-point: python -m envdiff <sub-command> …"""
from __future__ import annotations

import argparse
import sys

from envdiff import cli_diff, cli_reconcile, cli_snapshot, cli_lint, cli_template


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff, reconcile, lint and template .env files.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    cli_diff.build_parser(sub)
    cli_reconcile.build_parser(sub)
    cli_snapshot.build_parser(sub)
    cli_lint.build_parser(sub)
    cli_template.build_parser(sub)

    args = parser.parse_args(argv)

    dispatch = {
        "diff": cli_diff.run,
        "reconcile": cli_reconcile.run,
        "snapshot": cli_snapshot.run,
        "lint": cli_lint.run,
        "template": cli_template.run,
    }

    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
