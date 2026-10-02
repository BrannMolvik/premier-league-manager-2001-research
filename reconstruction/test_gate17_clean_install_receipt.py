import json
import os
import tempfile
import unittest
import zipfile
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate17_clean_install_receipt import (
    CleanInstallReceiptError,
    require_external_windows_11,
    validate_embedded_package_identity,
    write_clean_install_receipt,
)


COMMIT = "a" * 40
VERSION = "rc-test"
EXE = "FM2001-Windows11.exe"


def make_archive(path: Path, *, version=VERSION, commit=COMMIT, unsafe=False):
    manifest = {
        "schema_version": 1,
        "release_version": version,
        "repository_commit": commit,
        "external_original_game_data_bundled": False,
        "external_game_data_required_at_runtime": True,
        "executable": EXE,
        "files": [{"path": EXE, "size_bytes": 8, "sha256": "b" * 64}],
    }
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr(
            "FM2001-Windows11-rc/PACKAGE-MANIFEST.json",
            json.dumps(manifest),
        )
        bundle.writestr(f"FM2001-Windows11-rc/{EXE}", b"fake-exe")
        bundle.writestr(
            "FM2001-Windows11-rc/_internal/original_assets/MANIFEST.md",
            b"provenance",
        )
        if unsafe:
            bundle.writestr("../escape.txt", b"bad")
    return manifest


class Gate17CleanInstallReceiptTests(unittest.TestCase):
    def test_external_receipt_rejects_github_actions_even_on_windows_11(self):
        with (
            patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True),
            patch(
                "gate17_clean_install_receipt.require_windows_11",
                return_value={"platform": "Windows-11", "windows_build": 26200},
            ),
        ):
            with self.assertRaisesRegex(
                CleanInstallReceiptError,
                "cannot be produced by GitHub Actions",
            ):
                require_external_windows_11()

    def test_embedded_manifest_must_match_release_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "candidate.zip"
            make_archive(archive, version="wrong")
            with self.assertRaisesRegex(
                CleanInstallReceiptError,
                "different release version",
            ):
                validate_embedded_package_identity(
                    archive,
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    executable_name=EXE,
                )

    def test_clean_install_extracts_runs_smoke_and_writes_bound_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = root / "candidate.zip"
            make_archive(archive)
            install = root / "fresh-install"
            receipt = root / "receipts" / "clean_windows_install.json"
            installed_root = (
                install
                / "FM2001-Windows11-rc"
                / "_internal"
            )
            smoke = {
                "passed": True,
                "external_game_data_required": True,
                "application_root": str(installed_root),
                "source_root": str(installed_root / "original_assets" / "source"),
                "provenance_manifest": str(
                    installed_root / "original_assets" / "MANIFEST.md"
                ),
            }
            completed = SimpleNamespace(
                returncode=0,
                stdout=json.dumps(smoke) + "\n",
                stderr="",
            )
            with (
                patch(
                    "gate17_clean_install_receipt.require_external_windows_11",
                    return_value={"platform": "Windows-11", "windows_build": 26200},
                ),
                patch(
                    "gate17_clean_install_receipt.subprocess.run",
                    return_value=completed,
                ) as run,
            ):
                written = write_clean_install_receipt(
                    release_archive=archive,
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    install_dir=install,
                    output_path=receipt,
                    repo_root=repo,
                )

            self.assertEqual(written, receipt.resolve())
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertTrue(payload["windows_11"])
            self.assertTrue(payload["outside_development_environment"])
            self.assertTrue(payload["embedded_package_manifest_verified"])
            self.assertEqual(payload["repository_commit"], COMMIT)
            self.assertEqual(payload["release_version"], VERSION)
            self.assertEqual(payload["release_archive_sha256"], sha256(archive.read_bytes()).hexdigest())
            self.assertEqual(
                payload["installed_executable_relative_path"],
                f"FM2001-Windows11-rc/{EXE}",
            )
            args, kwargs = run.call_args
            self.assertEqual(args[0][1], "--package-smoke")
            self.assertEqual(kwargs["cwd"], install / "FM2001-Windows11-rc")

    def test_archive_path_traversal_fails_before_smoke_or_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = root / "candidate.zip"
            make_archive(archive, unsafe=True)
            receipt = root / "receipt.json"
            with (
                patch(
                    "gate17_clean_install_receipt.require_external_windows_11",
                    return_value={"platform": "Windows-11", "windows_build": 26200},
                ),
                patch("gate17_clean_install_receipt.subprocess.run") as run,
            ):
                with self.assertRaisesRegex(
                    CleanInstallReceiptError,
                    "unsafe path",
                ):
                    write_clean_install_receipt(
                        release_archive=archive,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        install_dir=root / "install",
                        output_path=receipt,
                        repo_root=repo,
                    )
            run.assert_not_called()
            self.assertFalse(receipt.exists())

    def test_receipt_never_overwrites_and_install_must_be_fresh(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = root / "candidate.zip"
            make_archive(archive)
            install = root / "install"
            install.mkdir()
            (install / "stale.txt").write_text("stale", encoding="utf-8")
            with patch(
                "gate17_clean_install_receipt.require_external_windows_11",
                return_value={"platform": "Windows-11", "windows_build": 26200},
            ):
                with self.assertRaisesRegex(CleanInstallReceiptError, "new or empty"):
                    write_clean_install_receipt(
                        release_archive=archive,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        install_dir=install,
                        output_path=root / "receipt.json",
                        repo_root=repo,
                    )


if __name__ == "__main__":
    unittest.main()
