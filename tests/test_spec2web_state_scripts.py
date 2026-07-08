from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "spec2web" / "scripts" / "init-state.py"
CHECK_SCRIPT = ROOT / "spec2web" / "scripts" / "check-state.py"


class Spec2WebStateScriptTests(unittest.TestCase):
    def test_init_creates_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state_dir = Path(tmp) / "spec2web"
            self.assertTrue((state_dir / "project-rules.md").exists())
            self.assertTrue((state_dir / "requirements-baseline.md").exists())
            self.assertTrue((state_dir / "system-design.md").exists())
            self.assertTrue((state_dir / "task-plan.md").exists())
            self.assertTrue((state_dir / "loop-state.md").exists())
            self.assertTrue((state_dir / "validation-log.md").exists())
            self.assertTrue((state_dir / "delivery-report.md").exists())

    def test_init_does_not_overwrite_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "spec2web"
            state_dir.mkdir()
            project_rules = state_dir / "project-rules.md"
            project_rules.write_text("custom content", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(project_rules.read_text(encoding="utf-8"), "custom content")
            self.assertIn("exists:", result.stdout)

    def test_check_state_passes_after_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [sys.executable, str(CHECK_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Spec2Web state check passed.", result.stdout)

    def test_check_state_fails_without_state_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CHECK_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing state directory", result.stdout)


if __name__ == "__main__":
    unittest.main()
