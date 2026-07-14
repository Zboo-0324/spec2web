#!/usr/bin/env python3
"""Inspect host capabilities and record the result via a state transaction."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from host_capabilities import (  # noqa: E402
    capabilities_to_json,
    capability_errors,
    inspect_local_capabilities,
    merge_host_report,
    parse_explicit_set,
)
from state_schema import resolve_state_dir, top_level_value  # noqa: E402
from state_transition import apply_transaction  # noqa: E402


def _read_loop_state(state_dir: Path) -> str:
    return (state_dir / "loop-state.md").read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect host capabilities and record the report.",
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Project directory containing the webbuilder state folder.",
    )
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        dest="explicit",
        help="Explicit capability in name=status:evidence form (repeatable).",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    state_dir = resolve_state_dir(target)
    if not state_dir.exists():
        print(f"missing state directory: {state_dir}", file=sys.stderr)
        return 1

    # Parse explicit host report entries.
    try:
        explicit = parse_explicit_set(args.explicit)
    except ValueError as exc:
        print(f"invalid --set argument: {exc}", file=sys.stderr)
        return 1

    # Probe local capabilities.
    inspected = inspect_local_capabilities(target)

    # Merge local probes with explicit host report.
    try:
        merged = merge_host_report(inspected, explicit)
    except ValueError as exc:
        print(f"host report validation failed: {exc}", file=sys.stderr)
        return 1

    # Read current state to determine required capabilities.
    loop_text = _read_loop_state(state_dir)
    raw_required = top_level_value(loop_text, "required_host_capabilities")
    required: set[str] = set()
    if raw_required and raw_required not in {"null", "none", "unknown"}:
        try:
            parsed = json.loads(raw_required)
            if isinstance(parsed, list):
                required = {str(item) for item in parsed}
        except json.JSONDecodeError:
            required = {item.strip() for item in raw_required.split(",") if item.strip()}

    # Evaluate required capabilities.
    errors = capability_errors(required, merged)

    # Build the state update.
    capabilities_json = capabilities_to_json(merged)
    current_revision = int(top_level_value(loop_text, "state_revision") or "0")

    updates: dict[str, str] = {}
    loop_update = _read_loop_state(state_dir)
    # Embed host capabilities as a JSON block in loop-state.md.
    block = f"## Host Capabilities\n\n```json\n{capabilities_json}\n```\n"

    # Replace or append the Host Capabilities section.
    import re

    section_pattern = re.compile(r"(?ms)^## Host Capabilities\s*\n.*?(?=^## |\Z)")
    if section_pattern.search(loop_update):
        loop_update = section_pattern.sub(block, loop_update)
    else:
        loop_update = loop_update.rstrip() + "\n\n" + block

    updates["loop-state.md"] = loop_update

    if errors:
        # Block execution when required capabilities fail.
        from state_schema import set_top_level_value

        loop_update = set_top_level_value(loop_update, "status", "blocked")
        loop_update = set_top_level_value(loop_update, "stop_reason", "environment_blocked")
        loop_update = set_top_level_value(loop_update, "resume_checkpoint", "initialization")
        updates["loop-state.md"] = loop_update

        apply_transaction(
            state_dir,
            "host-capability-check",
            updates,
            expected_revision=current_revision,
        )
        print("Host capability check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    apply_transaction(
        state_dir,
        "host-capability-check",
        updates,
        expected_revision=current_revision,
    )
    print("Host capability check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
