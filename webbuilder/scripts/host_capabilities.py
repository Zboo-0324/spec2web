"""Inspect local host capabilities and merge with explicit host reports."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


class _ImmutableTuple(tuple):
    """A tuple subclass that raises TypeError on mutation attempts."""

    def __setitem__(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def __delitem__(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def append(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def extend(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def insert(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def remove(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def pop(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def sort(self, *_: object, **__: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")

    def reverse(self, *_: object) -> None:
        raise TypeError("CAPABILITY_NAMES is immutable")


CAPABILITY_NAMES = _ImmutableTuple((
    "subagents",
    "browser",
    "git",
    "worktree",
    "docker",
    "network",
    "persistent_session",
))

VALID_CAPABILITY_STATUS = {"available", "unavailable", "unknown"}

# Capabilities whose inspected evidence says "requires host report".
# Explicit reports may only set these; local probes are never overridden.
_HOST_REPORT_ONLY = {"subagents", "browser", "network", "persistent_session"}


def inspect_local_capabilities(project_root: Path) -> dict[str, dict[str, str]]:
    """Probe local tools without network, Docker, or agent spawning.

    Returns a mapping from every ``CAPABILITY_NAMES`` entry to a dict
    with ``status`` and ``evidence`` keys.
    """
    git = shutil.which("git")
    docker = shutil.which("docker")
    return {
        "git": {
            "status": "available" if git else "unavailable",
            "evidence": "git executable probe",
        },
        "worktree": {
            "status": "available" if git and (project_root / ".git").exists() else "unavailable",
            "evidence": "Git repository and executable probe",
        },
        "docker": {
            "status": "available" if docker else "unavailable",
            "evidence": "docker executable probe",
        },
        "subagents": {"status": "unknown", "evidence": "requires host report"},
        "browser": {"status": "unknown", "evidence": "requires host report"},
        "network": {"status": "unknown", "evidence": "requires host report"},
        "persistent_session": {"status": "unknown", "evidence": "requires host report"},
    }


def _validate_capability_entry(name: str, entry: dict[str, str]) -> list[str]:
    """Return a list of validation errors for a single capability entry."""
    errors: list[str] = []
    if name not in CAPABILITY_NAMES:
        errors.append(f"unknown host capability: {name}")
        return errors
    status = entry.get("status")
    if status not in VALID_CAPABILITY_STATUS:
        allowed = ", ".join(sorted(VALID_CAPABILITY_STATUS))
        errors.append(f"host capability {name} status must be one of: {allowed}")
    evidence = entry.get("evidence")
    if not evidence or not str(evidence).strip():
        errors.append(f"host capability {name} requires nonempty evidence")
    return errors


def merge_host_report(
    inspected: dict[str, dict[str, str]],
    explicit: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Combine inspected local capabilities with an explicit host report.

    Explicit entries may only set capabilities whose inspected evidence
    says ``"requires host report"``.  Local observations (git, worktree,
    docker) are never overridden.

    Returns a fresh validated mapping covering all ``CAPABILITY_NAMES``.
    Raises ``ValueError`` when *explicit* contains invalid names, status
    values, or empty evidence.
    """
    errors: list[str] = []
    for name, entry in explicit.items():
        errors.extend(_validate_capability_entry(name, entry))
    if errors:
        raise ValueError("; ".join(errors))

    merged: dict[str, dict[str, str]] = {}
    for name in CAPABILITY_NAMES:
        local = inspected.get(name)
        if local is None:
            local = {"status": "unknown", "evidence": "not inspected"}
        merged[name] = dict(local)

    for name, entry in explicit.items():
        if name in _HOST_REPORT_ONLY:
            merged[name] = {"status": entry["status"], "evidence": str(entry["evidence"])}

    return merged


def capability_errors(
    required: set[str],
    capabilities: dict[str, dict[str, str]],
) -> list[str]:
    """Return sorted error strings for required capabilities that are not available.

    - ``unavailable`` => ``"required host capability unavailable: <name>"``
    - ``unknown`` or missing => ``"required host capability not confirmed: <name>"``
    - ``available`` => no error
    """
    errors: list[str] = []
    for name in sorted(required):
        entry = capabilities.get(name)
        if entry is None:
            errors.append(f"required host capability not confirmed: {name}")
            continue
        status = entry.get("status")
        if status == "available":
            continue
        if status == "unavailable":
            errors.append(f"required host capability unavailable: {name}")
        else:
            errors.append(f"required host capability not confirmed: {name}")
    return errors


# ---------------------------------------------------------------------------
# CLI helpers used by check-host.py
# ---------------------------------------------------------------------------

def parse_explicit_set(values: list[str]) -> dict[str, dict[str, str]]:
    """Parse ``--set name=status:evidence`` arguments into a capabilities dict."""
    result: dict[str, dict[str, str]] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"invalid --set format (expected name=status:evidence): {raw!r}")
        name, rest = raw.split("=", 1)
        name = name.strip()
        if ":" not in rest:
            raise ValueError(f"invalid --set format (expected status:evidence): {raw!r}")
        status, evidence = rest.split(":", 1)
        result[name] = {"status": status.strip(), "evidence": evidence.strip()}
    return result


def capabilities_to_json(capabilities: dict[str, dict[str, str]]) -> str:
    """Serialize capabilities to a JSON string suitable for embedding."""
    return json.dumps(capabilities, ensure_ascii=False, indent=2, sort_keys=True)
