"""Stand-alone entry point for `envdiff rotate` (used by __main__.py dispatch)."""
from __future__ import annotations

import sys

from envdiff.cli_rotate import build_parser, run


def main(argv: list[str] | None = None) -> int:
    """Parse *argv* and delegate to :func:`run`."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
