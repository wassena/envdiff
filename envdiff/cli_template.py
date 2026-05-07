"""CLI entry-point for the `envdiff template` sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.templater import template_from_file


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        description="Generate a .env.example template from a .env file."
    )
    if parent is not None:
        parser = parent.add_parser("template", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="envdiff template", **kwargs)

    parser.add_argument("env_file", help="Source .env file")
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Write result to FILE instead of stdout",
    )
    parser.add_argument(
        "--keep",
        metavar="KEY",
        nargs="*",
        default=[],
        help="Keys whose values should NOT be redacted",
    )
    parser.add_argument(
        "--placeholder",
        default="<REDACTED>",
        help="Replacement string for redacted values (default: <REDACTED>)",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Keep all values as-is (useful for non-secret envs)",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        result = template_from_file(
            args.env_file,
            redact=not args.no_redact,
            keep_values=args.keep,
            placeholder=args.placeholder,
        )
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    content = result.to_env_string()

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Template written to {args.output}")
    else:
        sys.stdout.write(content)

    return 0
