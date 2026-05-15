"""CLI entry point for the `envdiff compare` sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.comparator import compare_files, similarity_score, total_keys


def build_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    kwargs = dict(description="Compare two .env files and report differences.")
    if parent is not None:
        p = parent.add_parser("compare", **kwargs)
    else:
        p = argparse.ArgumentParser(**kwargs)
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument("--score", action="store_true", help="Print similarity score and exit")
    p.add_argument("--exit-code", action="store_true", help="Exit 1 when differences found")
    return p


def _format_text(result) -> str:
    lines: List[str] = []
    lines.append(f"Comparing: {result.source_a}  vs  {result.source_b}")
    lines.append(f"Total keys : {total_keys(result)}")
    lines.append(f"Common     : {len(result.common)}")
    lines.append(f"Only in A  : {len(result.only_in_a)}")
    lines.append(f"Only in B  : {len(result.only_in_b)}")
    lines.append(f"Changed    : {len(result.changed)}")
    lines.append(f"Similarity : {similarity_score(result):.2%}")
    if result.only_in_a:
        lines.append("\n[Only in A]")
        for k, v in sorted(result.only_in_a.items()):
            lines.append(f"  - {k}={v}")
    if result.only_in_b:
        lines.append("\n[Only in B]")
        for k, v in sorted(result.only_in_b.items()):
            lines.append(f"  + {k}={v}")
    if result.changed:
        lines.append("\n[Changed]")
        for k, (va, vb) in sorted(result.changed.items()):
            lines.append(f"  ~ {k}: {va!r} -> {vb!r}")
    return "\n".join(lines)


def _format_json(result) -> str:
    data = {
        "source_a": result.source_a,
        "source_b": result.source_b,
        "similarity": similarity_score(result),
        "total_keys": total_keys(result),
        "only_in_a": result.only_in_a,
        "only_in_b": result.only_in_b,
        "changed": {k: {"a": va, "b": vb} for k, (va, vb) in result.changed.items()},
        "common": result.common,
    }
    return json.dumps(data, indent=2)


def run(args: argparse.Namespace) -> int:
    try:
        result = compare_files(args.file_a, args.file_b)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.score:
        print(f"{similarity_score(result):.4f}")
        return 0

    output = _format_json(result) if args.fmt == "json" else _format_text(result)
    print(output)

    has_diff = bool(result.only_in_a or result.only_in_b or result.changed)
    return 1 if (args.exit_code and has_diff) else 0
