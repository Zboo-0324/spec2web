from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "webbuilder" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evidence_core import (  # noqa: E402
    MANIFEST_SCHEMA_VERSION,
    capture_command_evidence,
    git_fingerprint,
    load_manifest,
    promote_artifacts,
    redact_text,
    sha256_bytes,
    verify_manifest,
    write_manifest,
)


class EvidenceCoreTests(unittest.TestCase):
    def test_redacts_authorization_cookie_and_secret_assignment(self) -> None:
        raw = "Authorization: Bearer abc123\nCookie: sid=secret\nAPI_KEY=hunter2\n"
        redacted, replacements = redact_text(raw, explicit_secrets=["hunter2"])
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("sid=secret", redacted)
        self.assertNotIn("hunter2", redacted)
        self.assertGreaterEqual(replacements, 3)

    def test_manifest_round_trip_uses_project_relative_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "record_id": "EV-1",
                "run_id": "RUN-1",
                "subject_id": "TASK-001",
                "attempt": 1,
                "contract_revision": 1,
                "implementation_fingerprint": "sha256:" + "a" * 64,
                "command": ["python", "-m", "unittest"],
                "cwd": ".",
                "exit_code": 0,
                "tool_versions": {"python": "3.12"},
                "artifacts": [],
                "redaction": {"status": "passed", "replacements": 0},
                "result": "passed",
                "supersedes_record_id": None,
            }
            path = root / ".webbuilder-artifacts" / "RUN-1" / "TASK-001" / "1" / "manifest.json"
            write_manifest(path, manifest, project_root=root)
            self.assertEqual(load_manifest(path), manifest)
            self.assertNotIn(str(root), path.read_text(encoding="utf-8"))

    def test_git_fingerprint_uses_canonical_sha256_prefix_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "a.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
            fp = git_fingerprint(root)
            self.assertTrue(
                fp.startswith("sha256:"),
                f"fingerprint should start with 'sha256:' but got: {fp[:20]}...",
            )
            self.assertEqual(len(fp), len("sha256:") + 64)

    def test_git_fingerprint_includes_commit_and_dirty_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "a.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
            clean = git_fingerprint(root)
            (root / "a.txt").write_text("two\n", encoding="utf-8")
            dirty = git_fingerprint(root)
            self.assertNotEqual(clean, dirty)


class IdentifierValidationTests(unittest.TestCase):
    """run_id / subject_id must be plain path components — no escapes."""

    MALICIOUS_IDS = [
        ("../escape", "plain"),
        ("../../deep-escape", "plain"),
        ("RUN/../../escape", "contains separator"),
        ("/absolute/path", "absolute path"),
        (".", "dot"),
        ("..", "dot-dot"),
    ]

    def _make_root(self) -> Path:
        tmp = tempfile.mkdtemp()
        root = Path(tmp)
        (root / "src.txt").write_text("ok\n", encoding="utf-8")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        return root

    def test_rejects_malicious_run_id(self) -> None:
        for bad_id, label in self.MALICIOUS_IDS:
            with self.subTest(run_id=bad_id, reason=label):
                root = self._make_root()
                with self.assertRaises(ValueError, msg=f"run_id={bad_id!r} should be rejected"):
                    capture_command_evidence(
                        root, ["echo", "hi"],
                        run_id=bad_id,
                        subject_id="TASK-001",
                        attempt=1,
                        contract_revision=1,
                        allowed_paths=["src.txt"],
                    )

    def test_rejects_malicious_subject_id(self) -> None:
        for bad_id, label in self.MALICIOUS_IDS:
            with self.subTest(subject_id=bad_id, reason=label):
                root = self._make_root()
                with self.assertRaises(ValueError, msg=f"subject_id={bad_id!r} should be rejected"):
                    capture_command_evidence(
                        root, ["echo", "hi"],
                        run_id="RUN-1",
                        subject_id=bad_id,
                        attempt=1,
                        contract_revision=1,
                        allowed_paths=["src.txt"],
                    )

    def test_no_escaped_files_created(self) -> None:
        """Malicious IDs must not create files outside .webbuilder-artifacts."""
        for bad_id, label in self.MALICIOUS_IDS:
            with self.subTest(subject_id=bad_id, reason=label):
                root = self._make_root()
                try:
                    capture_command_evidence(
                        root, ["echo", "hi"],
                        run_id="RUN-1",
                        subject_id=bad_id,
                        attempt=1,
                        contract_revision=1,
                        allowed_paths=["src.txt"],
                    )
                except ValueError:
                    pass
                artifact_root = root / ".webbuilder-artifacts"
                if artifact_root.exists():
                    for child in artifact_root.rglob("*"):
                        resolved = child.resolve()
                        self.assertTrue(
                            resolved.is_relative_to(artifact_root.resolve()),
                            f"escaped file detected: {resolved}",
                        )


class CommandCaptureTests(unittest.TestCase):
    def test_failed_command_records_output_and_failed_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src.txt"
            source.write_text("tracked\n", encoding="utf-8")
            path = capture_command_evidence(
                root,
                [sys.executable, "-c", "import sys; print('boom'); sys.exit(7)"],
                run_id="RUN-1",
                subject_id="TASK-001",
                attempt=1,
                contract_revision=1,
                allowed_paths=["src.txt"],
            )
            manifest = load_manifest(path)
            self.assertEqual(manifest["exit_code"], 7)
            self.assertEqual(manifest["result"], "failed")
            output = path.with_name("command-output.txt").read_text(encoding="utf-8")
            self.assertIn("boom", output)

    def test_capture_redacts_explicit_secret(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src.txt").write_text("tracked\n", encoding="utf-8")
            path = capture_command_evidence(
                root,
                [sys.executable, "-c", "print('token-value')"],
                run_id="RUN-1",
                subject_id="PROJECT",
                attempt=1,
                contract_revision=1,
                allowed_paths=["src.txt"],
                explicit_secrets=["token-value"],
            )
            self.assertNotIn("token-value", path.with_name("command-output.txt").read_text(encoding="utf-8"))


class EvidenceVerificationTests(unittest.TestCase):
    """RED-phase tests: verify_manifest and promote_artifacts do not exist yet."""

    def capture_valid_manifest(self, root: Path, attempt: int = 1) -> Path:
        """Reusable fixture: capture a passing evidence manifest."""
        (root / "src.txt").write_text("tracked\n", encoding="utf-8")
        return capture_command_evidence(
            root,
            [sys.executable, "-c", "print('passed')"],
            run_id="RUN-1",
            subject_id="TASK-001",
            attempt=attempt,
            contract_revision=1,
            allowed_paths=["src.txt"],
        )

    def test_verify_rejects_artifact_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            fingerprint = str(manifest["implementation_fingerprint"])
            manifest_path.with_name("command-output.txt").write_text("tampered\n", encoding="utf-8")
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint=fingerprint,
            )
            self.assertIn(
                "evidence artifact hash mismatch: .webbuilder-artifacts/RUN-1/TASK-001/1/command-output.txt",
                errors,
            )

    def test_verify_rejects_old_contract_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=2,
                expected_fingerprint=str(manifest["implementation_fingerprint"]),
            )
            self.assertIn("evidence contract revision does not match", errors)

    def test_verify_rejects_wrong_implementation_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint="sha256:" + "0" * 64,
            )
            self.assertIn("evidence implementation fingerprint does not match", errors)

    def test_verify_rejects_failed_command_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src.txt").write_text("tracked\n", encoding="utf-8")
            manifest_path = capture_command_evidence(
                root,
                [sys.executable, "-c", "import sys; print('fail'); sys.exit(1)"],
                run_id="RUN-1",
                subject_id="TASK-001",
                attempt=1,
                contract_revision=1,
                allowed_paths=["src.txt"],
            )
            manifest = load_manifest(manifest_path)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint=str(manifest["implementation_fingerprint"]),
            )
            self.assertIn("evidence result is not passed", errors)

    def test_verify_rejects_failed_redaction_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            manifest["redaction"]["status"] = "failed"
            write_manifest(manifest_path, manifest, project_root=root)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint=str(manifest["implementation_fingerprint"]),
            )
            self.assertIn("evidence redaction did not pass", errors)

    def test_promote_copies_artifacts_and_rewrites_relative_paths(self) -> None:
        """promote_artifacts copies artifacts to destination and rewrites paths."""
        with tempfile.TemporaryDirectory() as worker_tmp:
            worker = Path(worker_tmp)
            manifest_path = self.capture_valid_manifest(worker)
            with tempfile.TemporaryDirectory() as main_tmp:
                main = Path(main_tmp)
                promoted_path = promote_artifacts(manifest_path, main)
                promoted = load_manifest(promoted_path)
                self.assertTrue(promoted_path.is_file())
                for artifact in promoted["artifacts"]:
                    self.assertTrue((main / artifact["path"]).is_file())
                    self.assertFalse(Path(artifact["path"]).is_absolute())
                self.assertIn("promoted_from", promoted)
                self.assertTrue(promoted["promoted_from"])
                self.assertFalse(Path(promoted["promoted_from"]).is_absolute())

    def test_verify_rejects_artifacts_list_with_non_mapping_entry(self) -> None:
        """verify_manifest must return errors (not raise) when artifacts contains a non-mapping."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            fingerprint = str(manifest["implementation_fingerprint"])
            manifest["artifacts"] = ["not-a-mapping"]
            write_manifest(manifest_path, manifest, project_root=root)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint=fingerprint,
            )
            self.assertIsInstance(errors, list, "verify_manifest must return a list, not raise")
            self.assertTrue(errors, "malformed artifacts entry must produce at least one error")

    def test_verify_rejects_redaction_that_is_not_a_mapping(self) -> None:
        """verify_manifest must return errors (not raise) when redaction is not a mapping."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            fingerprint = str(manifest["implementation_fingerprint"])
            manifest["redaction"] = "not-a-mapping"
            write_manifest(manifest_path, manifest, project_root=root)
            errors = verify_manifest(
                manifest_path,
                project_root=root,
                expected_contract_revision=1,
                expected_fingerprint=fingerprint,
            )
            self.assertIsInstance(errors, list, "verify_manifest must return a list, not raise")
            self.assertIn("evidence redaction did not pass", errors)

    def test_verify_rejects_absolute_and_escaping_artifact_paths(self) -> None:
        """verify_manifest rejects absolute or directory-escaping artifact paths."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self.capture_valid_manifest(root)
            manifest = load_manifest(manifest_path)
            fingerprint = str(manifest["implementation_fingerprint"])
            for invalid_path in ("/absolute/path.txt", "../outside.txt"):
                with self.subTest(invalid_path=invalid_path):
                    original_path = manifest["artifacts"][0]["path"]
                    manifest["artifacts"][0]["path"] = invalid_path
                    write_manifest(manifest_path, manifest, project_root=root)
                    errors = verify_manifest(
                        manifest_path,
                        project_root=root,
                        expected_contract_revision=1,
                        expected_fingerprint=fingerprint,
                    )
                    path_errors = [
                        e for e in errors
                        if "path" in e.lower() and ("invalid" in e.lower() or "escape" in e.lower())
                    ]
                    self.assertTrue(
                        path_errors,
                        f"Expected path-invalid/escape error for {invalid_path!r}, got: {errors}",
                    )
                    manifest["artifacts"][0]["path"] = original_path

    def test_promotion_rejects_tampered_source_before_creating_destination(self) -> None:
        """promote_artifacts must reject a manifest whose source artifact was tampered."""
        with tempfile.TemporaryDirectory() as worker_tmp:
            worker = Path(worker_tmp)
            manifest_path = self.capture_valid_manifest(worker)
            manifest = load_manifest(manifest_path)
            run_id = str(manifest["run_id"])
            subject_id = str(manifest["subject_id"])
            attempt = int(manifest["attempt"])

            # Tamper the worker's command-output.txt so its hash no longer matches.
            tampered_file = manifest_path.with_name("command-output.txt")
            tampered_file.write_text("tampered content\n", encoding="utf-8")

            with tempfile.TemporaryDirectory() as main_tmp:
                main = Path(main_tmp)
                dest_attempt_dir = main / ".webbuilder-artifacts" / run_id / subject_id / str(attempt)
                with self.assertRaises(ValueError):
                    promote_artifacts(manifest_path, main)
                self.assertFalse(
                    dest_attempt_dir.exists(),
                    "destination attempt directory must not exist after tampered-source rejection",
                )

    def test_promotion_rejects_escaping_artifact_path_without_writing_outside_destination(self) -> None:
        """promote_artifacts must reject an artifact path that escapes destination root."""
        with tempfile.TemporaryDirectory() as worker_tmp:
            worker = Path(worker_tmp)
            manifest_path = self.capture_valid_manifest(worker)

            # Place a secret file at worker parent level so the escaped path resolves.
            secret_source = worker.parent / "escaped.txt"
            secret_source.write_bytes(b"secret data")
            secret_sha = sha256_bytes(b"secret data")

            # Rewrite the manifest artifact to point at ../escaped.txt.
            manifest = load_manifest(manifest_path)
            manifest["artifacts"] = [{
                "path": "../escaped.txt",
                "sha256": secret_sha,
                "media_type": "text/plain",
                "size": len(b"secret data"),
            }]
            write_manifest(manifest_path, manifest, project_root=worker)

            with tempfile.TemporaryDirectory() as main_tmp:
                main = Path(main_tmp)
                escape_target = main.parent / "escaped.txt"
                original_exists = escape_target.exists()
                with self.assertRaises(ValueError):
                    promote_artifacts(manifest_path, main)
                self.assertFalse(
                    escape_target.exists() and not original_exists,
                    "escaped file must not be written outside destination root",
                )

    def test_promotion_rejects_preexisting_attempt_directory_without_overwriting(self) -> None:
        """promote_artifacts must reject promotion when destination attempt dir already exists."""
        with tempfile.TemporaryDirectory() as worker_tmp:
            worker = Path(worker_tmp)
            manifest_path = self.capture_valid_manifest(worker)
            manifest = load_manifest(manifest_path)
            run_id = str(manifest["run_id"])
            subject_id = str(manifest["subject_id"])
            attempt = int(manifest["attempt"])

            with tempfile.TemporaryDirectory() as main_tmp:
                main = Path(main_tmp)
                dest_attempt_dir = main / ".webbuilder-artifacts" / run_id / subject_id / str(attempt)
                dest_attempt_dir.mkdir(parents=True, exist_ok=True)
                sentinel = dest_attempt_dir / "sentinel.txt"
                sentinel.write_text("original", encoding="utf-8")

                with self.assertRaises(ValueError):
                    promote_artifacts(manifest_path, main)
                self.assertEqual(
                    sentinel.read_text(encoding="utf-8"),
                    "original",
                    "sentinel file must not be overwritten by promote_artifacts",
                )

    def test_promote_is_idempotent_and_rejects_divergent_destination(self) -> None:
        """promote_artifacts is idempotent but rejects divergent destination files."""
        with tempfile.TemporaryDirectory() as worker_tmp:
            worker = Path(worker_tmp)
            manifest_path = self.capture_valid_manifest(worker)
            with tempfile.TemporaryDirectory() as main_tmp:
                main = Path(main_tmp)
                promoted_path1 = promote_artifacts(manifest_path, main)
                promoted_path2 = promote_artifacts(manifest_path, main)
                self.assertEqual(promoted_path1, promoted_path2)
                promoted1 = load_manifest(promoted_path1)
                promoted2 = load_manifest(promoted_path2)
                for a1, a2 in zip(promoted1["artifacts"], promoted2["artifacts"]):
                    self.assertEqual(
                        (main / a1["path"]).read_bytes(),
                        (main / a2["path"]).read_bytes(),
                    )

                # Diverge the command-output artifact in the destination.
                target_artifact = None
                for artifact in promoted2["artifacts"]:
                    if "command-output" in artifact["path"]:
                        target_artifact = artifact
                        break
                self.assertIsNotNone(target_artifact, "No command-output artifact found to diverge")
                divergent_bytes = b"divergent data"
                (main / target_artifact["path"]).write_bytes(divergent_bytes)

                with self.assertRaises(ValueError):
                    promote_artifacts(manifest_path, main)
                self.assertEqual(
                    (main / target_artifact["path"]).read_bytes(),
                    divergent_bytes,
                )


if __name__ == "__main__":
    unittest.main()
