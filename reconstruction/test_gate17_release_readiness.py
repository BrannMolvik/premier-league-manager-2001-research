"""Synthetic tests for the fail-closed Gate-17 release evidence contract."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from gate17_release_readiness import (
    ReleaseReadinessError,
    parse_release_evidence,
    require_path_outside_repo,
    validate_external_receipts,
    validate_limitations_document,
    validate_release_archive,
    validate_roadmap_prerequisites,
)


COMMIT = "a" * 40
RELEASE_VERSION = "test-1"
RELEASE_ARCHIVE_BYTES = b"release bytes"
RELEASE_ARCHIVE_SHA256 = sha256(RELEASE_ARCHIVE_BYTES).hexdigest()


def write_receipt(path, **flags):
    payload = {
        "passed": True,
        "repository_commit": COMMIT,
        "release_version": RELEASE_VERSION,
        "release_archive_sha256": RELEASE_ARCHIVE_SHA256,
        **flags,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return sha256(path.read_bytes()).hexdigest()


def write_roadmap(path, *, open_gate=None, omit_gate=None):
    lines = ["# Roadmap", ""]
    for gate in range(1, 18):
        if gate == omit_gate:
            continue
        lines.append(f"## Gate {gate} - Synthetic")
        lines.append("")
        marker = " " if gate == open_gate else "x"
        lines.append(f"- [{marker}] criterion {gate}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


class Gate17ReleaseReadinessTests(unittest.TestCase):
    def fixture(self, temp):
        temp = Path(temp)
        repo = temp / "repo"
        repo.mkdir()
        limitations = repo / "research/RELEASE_LIMITATIONS.md"
        limitations.parent.mkdir(parents=True)
        limitations.write_text(
            "# Release limitations\\n\\n"
            + "Known accepted limitation. " * 20,
            encoding="utf-8",
        )

        private = temp / "private"
        receipts = {}
        receipt_flags = {
            "clean_windows_install": {
                "windows_11": True,
                "outside_development_environment": True,
            },
            "new_game_management_loop": {
                "new_game": True,
                "management_loop": True,
            },
            "season_progression": {
                "season_progression": True,
            },
            "save_reload": {
                "save_reload": True,
            },
        }
        for name, flags in receipt_flags.items():
            path = private / f"{name}.json"
            receipts[name] = {
                "path": str(path),
                "sha256": write_receipt(path, **flags),
            }

        archive = private / "fm2001-port.zip"
        archive.write_bytes(RELEASE_ARCHIVE_BYTES)
        evidence = {
            "schema_version": 1,
            "release_version": RELEASE_VERSION,
            "repository_commit": COMMIT,
            "limitations_path": "research/RELEASE_LIMITATIONS.md",
            "external_receipts": receipts,
            "archive": {
                "sha256": RELEASE_ARCHIVE_SHA256,
                "size_bytes": archive.stat().st_size,
            },
        }
        return repo, private, archive, evidence

    def test_roadmap_prerequisites_allow_open_gate17_only(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", open_gate=17)

            result = validate_roadmap_prerequisites(repo)

            self.assertTrue(result["all_prerequisites_complete"])
            self.assertEqual(result["required_gates"], list(range(1, 17)))
            self.assertNotIn("17", result["criteria"])

    def test_roadmap_prerequisites_reject_any_open_gate_1_through_16(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", open_gate=13)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                r"Gate 13 \(1 unchecked\)",
            ):
                validate_roadmap_prerequisites(repo)

    def test_roadmap_prerequisites_reject_missing_gate_section(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", omit_gate=14)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "missing prerequisite gate sections: \\[14\\]",
            ):
                validate_roadmap_prerequisites(repo)

    def test_complete_external_evidence_and_archive_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, archive, raw = self.fixture(temp)
            evidence = parse_release_evidence(raw)
            checked = validate_external_receipts(evidence, repo)
            self.assertEqual(set(checked), set(raw["external_receipts"]))
            archive_check = validate_release_archive(
                archive, evidence.archive, repo
            )
            self.assertEqual(archive_check["size_bytes"], len(RELEASE_ARCHIVE_BYTES))
            limits = validate_limitations_document(
                repo, evidence.limitations_path
            )
            self.assertGreater(limits["characters"], 200)

    def test_missing_or_false_windows_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            evidence = parse_release_evidence(raw)
            descriptor = evidence.external_receipts["clean_windows_install"]
            path = Path(descriptor.path)
            write_receipt(
                path,
                windows_11=True,
                outside_development_environment=False,
            )
            mutable = dict(raw)
            mutable["external_receipts"] = dict(raw["external_receipts"])
            mutable["external_receipts"]["clean_windows_install"] = {
                "path": str(path),
                "sha256": sha256(path.read_bytes()).hexdigest(),
            }
            evidence = parse_release_evidence(mutable)
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "outside_development_environment",
            ):
                validate_external_receipts(evidence, repo)

    def test_external_receipts_must_be_four_distinct_files(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            shared = raw["external_receipts"]["clean_windows_install"]
            raw["external_receipts"]["new_game_management_loop"] = dict(shared)
            evidence = parse_release_evidence(raw)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "reuses the same evidence file",
            ):
                validate_external_receipts(evidence, repo)

    def test_receipt_for_another_release_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "season_progression"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["release_version"] = "other-release"
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different release version",
            ):
                validate_external_receipts(parse_release_evidence(raw), repo)

    def test_receipt_for_another_release_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "save_reload"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["release_archive_sha256"] = "b" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different release archive",
            ):
                validate_external_receipts(parse_release_evidence(raw), repo)

    def test_receipt_for_another_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "save_reload"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["repository_commit"] = "b" * 40
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()
            evidence = parse_release_evidence(raw)
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different repository commit",
            ):
                validate_external_receipts(evidence, repo)

    def test_release_archive_and_receipts_must_stay_outside_git(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, _raw = self.fixture(temp)
            inside = repo / "release.zip"
            inside.write_bytes(b"x")
            with self.assertRaisesRegex(
                ReleaseReadinessError, "outside the Git repository"
            ):
                require_path_outside_repo(inside, repo, label="release archive")

    def test_pre_release_limitations_document_cannot_pass_final_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            path = repo / raw["limitations_path"]
            path.write_text(
                "# Release limitations\\n\\nPRE-RELEASE working list. "
                + "Still pending. " * 30,
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReleaseReadinessError, "pre-release"):
                validate_limitations_document(repo, raw["limitations_path"])

    def test_evidence_schema_requires_exact_receipt_set_and_archive_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            _repo, _private, _archive, raw = self.fixture(temp)
            raw["external_receipts"].pop("save_reload")
            with self.assertRaisesRegex(
                ReleaseReadinessError, "receipt set mismatch"
            ):
                parse_release_evidence(raw)


if __name__ == "__main__":
    unittest.main()
