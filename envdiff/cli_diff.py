"""CLI entry point for diffing two .env files."""

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs, has_differences
from envdiff.formatter import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff two .env files and report differences.",
    )
    parser.add_argument("file_a", help="Base .env file (e.g. .env.example)")
    parser.add_argument("file_b", help="Target .env file (e.g. .env)")
    parser.add_argument(
        "--format",
        choices=["text", "json", "dotenv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(env_a, env_b)
    output = render(result, fmt=args.format)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
    else:
        print(output)

    if args.exit_code and has_differences(result):
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
