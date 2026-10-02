import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from gate17_release_evidence import (
    ReleaseEvidenceAssemblerError,
    assemble_release_evidence,
)


COMMIT = "a" * 40
VERSION = "rc-test"


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


class Gate17ReleaseEvidenceAssemblerTests(unittest.TestCase):
    def _receipt(
        self,
        path: Path,
        *,
        archive_sha: str,
        kind: str,
        release_version: str = VERSION,
        repository_commit: str = COMMIT,
    ) -> Path:
        flags = {
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
        payload = {
            "passed": True,
            "release_version": release_version,
            "repository_commit": repository_commit,
            "release_archive_sha256": archive_sha,
            "windows_11": True,
            "windows_build": 26200,
            "windows_product_type": 1,
            **flags[kind],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _fixture(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        repo = root / "repo"
        repo.mkdir()
        archive = root / "release.zip"
        archive.write_bytes(b"candidate")
        archive_sha = digest(archive.read_bytes())
        receipts = {}
        for name in (
            "clean_windows_install",
            "new_game_management_loop",
            "season_progression",
            "save_reload",
        ):
            receipts[name] = self._receipt(
                root / f"{name}.json",
                archive_sha=archive_sha,
                kind=name,
            )
        return repo, archive, receipts

    def test_assembler_hashes_and_prevalidates_exact_archive_and_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)
            output = root / "release-evidence.json"

            result = assemble_release_evidence(
                release_version=VERSION,
                repository_commit=COMMIT,
                release_archive=archive,
                receipt_paths=receipts,
                output_path=output,
                repo_root=repo,
            )

            self.assertEqual(result, output.resolve())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["release_version"], VERSION)
            self.assertEqual(payload["repository_commit"], COMMIT)
            self.assertEqual(
                payload["limitations_path"],
                "research/RELEASE_LIMITATIONS.md",
            )
            self.assertEqual(payload["archive"]["sha256"], digest(b"candidate"))
            self.assertEqual(payload["archive"]["size_bytes"], len(b"candidate"))
            self.assertEqual(
                set(payload["external_receipts"]),
                set(receipts),
            )
            for name, path in receipts.items():
                self.assertEqual(
                    payload["external_receipts"][name]["sha256"],
                    digest(path.read_bytes()),
                )

    def test_mismatched_receipt_archive_identity_fails_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)
            self._receipt(
                receipts["save_reload"],
                archive_sha="0" * 64,
                kind="save_reload",
            )
            output = root / "release-evidence.json"

            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "different release archive",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=output,
                    repo_root=repo,
                )

            self.assertFalse(output.exists())

    def test_missing_required_flag_and_commit_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)
            bad = json.loads(
                receipts["new_game_management_loop"].read_text(encoding="utf-8")
            )
            bad.pop("management_loop")
            receipts["new_game_management_loop"].write_text(
                json.dumps(bad),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "management_loop",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=root / "flags.json",
                    repo_root=repo,
                )

            repo2, archive2, receipts2 = self._fixture(root / "other")
            self._receipt(
                receipts2["save_reload"],
                archive_sha=digest(archive2.read_bytes()),
                kind="save_reload",
                repository_commit="b" * 40,
            )
            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "different repository commit",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive2,
                    receipt_paths=receipts2,
                    output_path=(root / "other" / "commit.json"),
                    repo_root=repo2,
                )

    def test_duplicate_receipt_path_and_bad_receipt_set_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)
            receipts["save_reload"] = receipts["season_progression"]
            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "reuses the same file",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=root / "dup.json",
                    repo_root=repo,
                )

            _, _, fresh = self._fixture(root / "fresh")
            fresh.pop("save_reload")
            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "receipt set mismatch",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=root / "fresh" / "release.zip",
                    receipt_paths=fresh,
                    output_path=root / "fresh" / "missing.json",
                    repo_root=root / "fresh" / "repo",
                )

    def test_receipt_cannot_reuse_release_archive_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)
            receipts["save_reload"] = archive

            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "cannot reuse the release archive",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=root / "evidence.json",
                    repo_root=repo,
                )

    def test_output_must_be_outside_repo_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, archive, receipts = self._fixture(root)

            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "outside",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=repo / "evidence.json",
                    repo_root=repo,
                )

            output = root / "existing.json"
            output.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(
                ReleaseEvidenceAssemblerError,
                "do not overwrite",
            ):
                assemble_release_evidence(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    receipt_paths=receipts,
                    output_path=output,
                    repo_root=repo,
                )


if __name__ == "__main__":
    unittest.main()
