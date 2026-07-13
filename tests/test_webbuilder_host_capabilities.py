from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "webbuilder" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from host_capabilities import (  # noqa: E402
    CAPABILITY_NAMES,
    capability_errors,
    inspect_local_capabilities,
    merge_host_report,
)


class HostCapabilityErrorTests(unittest.TestCase):
    """capability_errors must block on unavailable or unknown required caps."""

    def test_required_browser_unavailable_blocks(self) -> None:
        capabilities = {"browser": {"status": "unavailable", "evidence": "host report"}}
        self.assertEqual(
            capability_errors({"browser"}, capabilities),
            ["required host capability unavailable: browser"],
        )

    def test_unknown_required_capability_does_not_pass(self) -> None:
        capabilities = {"browser": {"status": "unknown", "evidence": "not inspected"}}
        self.assertEqual(
            capability_errors({"browser"}, capabilities),
            ["required host capability not confirmed: browser"],
        )

    def test_required_available_capability_produces_no_errors(self) -> None:
        capabilities = {"git": {"status": "available", "evidence": "git --version"}}
        self.assertEqual(capability_errors({"git"}, capabilities), [])

    def test_multiple_required_failures_all_reported(self) -> None:
        capabilities = {
            "browser": {"status": "unavailable", "evidence": "host report"},
            "subagents": {"status": "unknown", "evidence": "not inspected"},
        }
        errors = capability_errors({"browser", "subagents"}, capabilities)
        self.assertIn("required host capability unavailable: browser", errors)
        self.assertIn("required host capability not confirmed: subagents", errors)

    def test_optional_missing_capability_does_not_block(self) -> None:
        capabilities = {"docker": {"status": "unavailable", "evidence": "not installed"}}
        self.assertEqual(capability_errors(set(), capabilities), [])

    def test_empty_required_set_returns_no_errors(self) -> None:
        capabilities = {"browser": {"status": "unavailable", "evidence": "host report"}}
        self.assertEqual(capability_errors(set(), capabilities), [])


class MergeHostReportTests(unittest.TestCase):
    """merge_host_report must combine inspected and explicit capabilities."""

    def test_explicit_host_report_overrides_only_non_local_capabilities(self) -> None:
        inspected = {"git": {"status": "available", "evidence": "git --version"}}
        explicit = {"browser": {"status": "available", "evidence": "Codex browser tool listed"}}
        merged = merge_host_report(inspected, explicit)
        self.assertEqual(merged["git"]["status"], "available")
        self.assertEqual(merged["browser"]["status"], "available")

    def test_explicit_report_does_not_override_inspected_local_capability(self) -> None:
        inspected = {"git": {"status": "available", "evidence": "git --version"}}
        explicit = {"git": {"status": "unavailable", "evidence": "user says no"}}
        merged = merge_host_report(inspected, explicit)
        self.assertEqual(merged["git"]["status"], "available")

    def test_merge_preserves_all_inspected_capabilities(self) -> None:
        inspected = {
            "git": {"status": "available", "evidence": "git --version"},
            "docker": {"status": "unavailable", "evidence": "docker not found"},
        }
        explicit: dict[str, dict[str, str]] = {}
        merged = merge_host_report(inspected, explicit)
        self.assertEqual(merged["git"]["status"], "available")
        self.assertEqual(merged["docker"]["status"], "unavailable")


class InspectLocalCapabilitiesTests(unittest.TestCase):
    """inspect_local_capabilities probes local tools without network or Docker."""

    def test_returns_all_known_capability_names(self) -> None:
        with self.subTest():
            caps = inspect_local_capabilities(Path(__file__).resolve().parents[1])
            for name in CAPABILITY_NAMES:
                self.assertIn(name, caps, f"missing capability: {name}")

    def test_git_and_worktree_available_in_git_repo(self) -> None:
        caps = inspect_local_capabilities(Path(__file__).resolve().parents[1])
        self.assertEqual(caps["git"]["status"], "available")
        self.assertEqual(caps["worktree"]["status"], "available")

    def test_subagents_browser_network_persistent_session_require_host_report(self) -> None:
        caps = inspect_local_capabilities(Path(__file__).resolve().parents[1])
        for name in ("subagents", "browser", "network", "persistent_session"):
            self.assertEqual(
                caps[name]["status"],
                "unknown",
                f"{name} must be unknown until host reports it",
            )

    def test_capability_names_tuple_is_immutable(self) -> None:
        self.assertIsInstance(CAPABILITY_NAMES, tuple)
        with self.assertRaises(TypeError):
            CAPABILITY_NAMES.append("new")  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
