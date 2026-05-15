"""Standalone entry point for `envdiff-compare`."""
import sys

from envdiff.cli_compare import build_parser, run


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
