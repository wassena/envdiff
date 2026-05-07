"""Entry-point: python -m envdiff <sub-command> [args]"""

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: envdiff <diff|reconcile|snapshot> [options]")
        sys.exit(1)

    cmd, rest = sys.argv[1], sys.argv[2:]

    if cmd == "diff":
        from envdiff.cli_diff import run
    elif cmd == "reconcile":
        from envdiff.cli_reconcile import run
    elif cmd == "snapshot":
        from envdiff.cli_snapshot import run
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print("available commands: diff, reconcile, snapshot", file=sys.stderr)
        sys.exit(1)

    sys.exit(run(rest))


if __name__ == "__main__":
    main()
