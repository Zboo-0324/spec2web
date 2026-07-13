"""Contract-level tests for the autonomous reference e2e evidence surface.

Verifies that the maintained reference application exposes the browser,
accessibility, and performance evidence methods required by the autonomous
delivery plan.  These tests import modules and inspect structure without
launching a browser or Django server.
"""
from __future__ import annotations

import importlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTONOMOUS_DIR = ROOT / "examples" / "autonomous-reference"


class AutonomousE2EContractTests(unittest.TestCase):
    """Verify the e2e evidence surface is structurally complete."""

    @classmethod
    def setUpClass(cls) -> None:
        """Import e2e modules from the autonomous-reference example."""
        import sys

        # Add the autonomous-reference directory so ``e2e`` package resolves.
        cls._orig_path = sys.path[:]
        sys.path.insert(0, str(AUTONOMOUS_DIR))

        # The e2e modules import playwright at module level.  When running
        # from the root test suite (``python -m unittest discover``) playwright
        # is not installed — skip the entire class rather than erroring.
        try:
            cls.e2e_package = importlib.import_module("e2e")
            cls.server_module = importlib.import_module("e2e.server")
            cls.accessibility_module = importlib.import_module("e2e.accessibility")
            cls.test_module = importlib.import_module("e2e.test_primary_flow")
        except ImportError:
            sys.path[:] = cls._orig_path
            raise unittest.SkipTest("playwright not installed — skipping contract tests")

    @classmethod
    def tearDownClass(cls) -> None:
        import sys

        sys.path[:] = cls._orig_path

    # -- module existence ---------------------------------------------------

    def test_e2e_package_has_docstring(self) -> None:
        """The e2e package must have a module docstring."""
        self.assertTrue(self.e2e_package.__doc__)

    def test_server_module_exports_live_server(self) -> None:
        """e2e.server must expose a LiveServer class."""
        self.assertTrue(hasattr(self.server_module, "LiveServer"))
        self.assertTrue(
            callable(self.server_module.LiveServer),
            "LiveServer must be a callable (class)",
        )

    def test_accessibility_module_exports_baseline_function(self) -> None:
        """e2e.accessibility must expose baseline_accessibility_failures."""
        func = getattr(self.accessibility_module, "baseline_accessibility_failures", None)
        self.assertTrue(callable(func), "baseline_accessibility_failures must be callable")

    # -- test class contract ------------------------------------------------

    def test_primary_flow_class_exists(self) -> None:
        """e2e.test_primary_flow must contain PrimaryFlowTests."""
        cls = getattr(self.test_module, "PrimaryFlowTests", None)
        self.assertIsNotNone(cls, "PrimaryFlowTests class not found in e2e.test_primary_flow")
        self.assertTrue(issubclass(cls, unittest.TestCase))

    def test_primary_flow_has_browser_test(self) -> None:
        """PrimaryFlowTests must have the browser primary-flow test method."""
        cls = self.test_module.PrimaryFlowTests
        self.assertTrue(
            hasattr(cls, "test_login_create_complete_and_responsive_layout"),
            "missing test_login_create_complete_and_responsive_layout",
        )

    def test_primary_flow_has_accessibility_test(self) -> None:
        """PrimaryFlowTests must have the accessibility states test method."""
        cls = self.test_module.PrimaryFlowTests
        self.assertTrue(
            hasattr(cls, "test_accessibility_states"),
            "missing test_accessibility_states",
        )

    def test_primary_flow_has_performance_test(self) -> None:
        """PrimaryFlowTests must have the warm-flow performance budget test."""
        cls = self.test_module.PrimaryFlowTests
        self.assertTrue(
            hasattr(cls, "test_warm_primary_flow_under_budget"),
            "missing test_warm_primary_flow_under_budget",
        )

    # -- evidence capture invocation path -----------------------------------

    def test_capture_evidence_script_exists(self) -> None:
        """capture-evidence.py must exist in webbuilder/scripts/."""
        script = ROOT / "webbuilder" / "scripts" / "capture-evidence.py"
        self.assertTrue(script.is_file(), f"missing {script.relative_to(ROOT)}")

    def test_evidence_core_importable(self) -> None:
        """webbuilder/scripts/evidence_core.py must be importable."""
        import sys

        scripts_dir = str(ROOT / "webbuilder" / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        try:
            mod = importlib.import_module("evidence_core")
            self.assertTrue(
                hasattr(mod, "capture_command_evidence"),
                "evidence_core must expose capture_command_evidence",
            )
        finally:
            if scripts_dir in sys.path:
                sys.path.remove(scripts_dir)


if __name__ == "__main__":
    unittest.main()
