"""Formatters for rendering diff results to the terminal or other outputs."""

from typing import Literal
from envdiff.differ import DiffResult

OutputFormat = Literal["text", "json", "dotenv"]


def format_text(result: DiffResult, env_a_label: str = "env_a", env_b_label: str = "env_b") -> str:
    """Render a DiffResult as a human-readable text diff."""
    lines: list[str] = []

    if result.missing_in_b:
        lines.append(f"Keys in [{env_a_label}] but missing in [{env_b_label}]:")
        for key in sorted(result.missing_in_b):
            lines.append(f"  - {key}={result.only_in_a[key]}")
        lines.append("")

    if result.missing_in_a:
        lines.append(f"Keys in [{env_b_label}] but missing in [{env_a_label}]:")
        for key in sorted(result.missing_in_a):
            lines.append(f"  + {key}={result.only_in_b[key]}")
        lines.append("")

    if result.changed:
        lines.append("Changed values:")
        for key in sorted(result.changed):
            val_a, val_b = result.changed[key]
            lines.append(f"  ~ {key}")
            lines.append(f"      {env_a_label}: {val_a}")
            lines.append(f"      {env_b_label}: {val_b}")
        lines.append("")

    if not result.missing_in_a and not result.missing_in_b and not result.changed:
        lines.append("No differences found.")

    return "\n".join(lines).rstrip()


def format_json(result: DiffResult, env_a_label: str = "env_a", env_b_label: str = "env_b") -> str:
    """Render a DiffResult as a JSON string."""
    import json

    payload = {
        f"missing_in_{env_b_label}": {
            k: result.only_in_a[k] for k in sorted(result.missing_in_b)
        },
        f"missing_in_{env_a_label}": {
            k: result.only_in_b[k] for k in sorted(result.missing_in_a)
        },
        "changed": {
            k: {env_a_label: v[0], env_b_label: v[1]}
            for k, v in sorted(result.changed.items())
        },
    }
    return json.dumps(payload, indent=2)


def format_dotenv(result: DiffResult) -> str:
    """Render a merged .env snippet containing only differing / missing keys."""
    lines: list[str] = []

    for key in sorted(result.missing_in_a):
        lines.append(f"{key}={result.only_in_b[key]}")

    for key in sorted(result.changed):
        _, val_b = result.changed[key]
        lines.append(f"{key}={val_b}")

    return "\n".join(lines)


def render(result: DiffResult, fmt: OutputFormat = "text",
           env_a_label: str = "env_a", env_b_label: str = "env_b") -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_json(result, env_a_label, env_b_label)
    if fmt == "dotenv":
        return format_dotenv(result)
    return format_text(result, env_a_label, env_b_label)
