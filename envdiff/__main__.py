"""Entry point: python -m envdiff <subcommand>."""
from __future__ import annotations

import argparse
import sys

import envdiff.cli_diff as cli_diff
import envdiff.cli_lint as cli_lint
import envdiff.cli_mask as cli_mask
import envdiff.cli_reconcile as cli_reconcile
import envdiff.cli_snapshot as cli_snapshot
import envdiff.cli_template as cli_template


_SUBCOMMANDS = [
    cli_diff,
    cli_lint,
    cli_mask,
    cli_reconcile,
    cli_snapshot,
    cli_template,
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff, reconcile, lint, mask, and manage .env files.",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    for mod in _SUBCOMMANDS:
        mod.build_parser(sub)

    args = parser.parse_args(argv)

    if args.subcommand is None:
        parser.print_help()
        return 0

    return _SUBCOMMANDS[
        [m.__name__.split(".")[-1].replace("cli_", "") for m in _SUBCOMMANDS].index(
            args.subcommand
        )
    ].run(args)


if __name__ == "__main__":
    sys.exit(main())
