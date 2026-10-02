import json
import tempfile
import unittest
import zipfile
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate17_clean_windows_install import (
    CleanWindowsInstallReceiptError,
    _preflight_archive,
    require_external_windows_11_workstation,
    run_clean_windows_install_receipt,
    validate_installed_payload,
)
from gate17_release_readiness import ReleaseReadinessError


COMMIT = "a" * 40
VERSION = "rc-test"


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


class Gate17CleanWindowsInstallReceiptTests(unittest.TestCase):
    def _archive(self, root: Path, *, bad_hash: bool = False) -> Path:
        archive = root / "candidate.zip"
        exe = b"fake-frozen-exe"
        readme = b"release readme"
        manifest = {
            "schema_version": 1,
            "release_version": VERSION,
            "repository_commit": COMMIT,
            "external_original_game_data_bundled": False,
            "external_game_data_required_at_runtime": True,
            "executable": "FM2001-Windows11.exe",
            "files": [
                {
                    "path": "FM2001-Windows11.exe",
                    "size_bytes": len(exe),
                    "sha256": ("0" * 64 if bad_hash else digest(exe)),
                },
                {
                    "path": "README-RELEASE.txt",
                    "size_bytes": len(readme),
                    "sha256": digest(readme),
                },
            ],
        }
        top = f"FM2001-Windows11-{VERSION}"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(f"{top}/FM2001-Windows11.exe", exe)
            zf.writestr(f"{top}/README-RELEASE.txt", readme)
            zf.writestr(
                f"{top}/PACKAGE-MANIFEST.json",
                json.dumps(manifest, sort_keys=True),
            )
        return archive

    def test_success_extracts_fresh_package_validates_payload_and_writes_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = self._archive(root)
            install = root / "clean-install"
            receipts = root / "receipts"

            completed = SimpleNamespace(
                returncode=0,
                stdout="PACKAGE_SMOKE_OK\n",
            )
            with (
                patch(
                    "gate17_clean_windows_install.require_external_windows_11_workstation",
                    return_value={
                        "platform": "Windows-11-10.0.26200",
                        "windows_build": 26200,
                    },
                ),
                patch(
                    "gate17_clean_windows_install.subprocess.run",
                    return_value=completed,
                ) as runner,
            ):
                receipt = run_clean_windows_install_receipt(
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    install_root=install,
                    output_dir=receipts,
                    repo_root=repo,
                )

            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertTrue(payload["windows_11"])
            self.assertTrue(payload["outside_development_environment"])
            self.assertEqual(payload["repository_commit"], COMMIT)
            self.assertEqual(payload["release_version"], VERSION)
            self.assertEqual(payload["release_archive_sha256"], digest(archive.read_bytes()))
            self.assertEqual(payload["validated_payload_file_count"], 2)
            self.assertEqual(payload["package_smoke_returncode"], 0)
            self.assertEqual(payload["windows_build"], 26200)
            self.assertTrue(Path(payload["package_root"]).is_relative_to(install.resolve()))
            runner.assert_called_once()
            args, kwargs = runner.call_args
            self.assertEqual(args[0][1], "--package-smoke")
            self.assertEqual(Path(kwargs["cwd"]), Path(payload["package_root"]))

    def test_external_windows_guard_rejects_github_actions_and_server(self):
        base = {"platform": "Windows-11", "windows_build": 26200}

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict("gate17_release_readiness.os.environ", {"GITHUB_ACTIONS": "true"}, clear=False),
        ):
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "GitHub Actions",
            ):
                require_external_windows_11_workstation()

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict("gate17_release_readiness.os.environ", {}, clear=True),
            patch(
                "gate17_release_readiness.sys.getwindowsversion",
                return_value=SimpleNamespace(product_type=3),
                create=True,
            ),
        ):
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "client workstation",
            ):
                require_external_windows_11_workstation()

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict("gate17_release_readiness.os.environ", {}, clear=True),
            patch(
                "gate17_release_readiness.sys.getwindowsversion",
                return_value=SimpleNamespace(product_type=1),
                create=True,
            ),
        ):
            result = require_external_windows_11_workstation()

        self.assertEqual(result["windows_product_type"], 1)
        self.assertEqual(result["windows_build"], 26200)

    def test_windows_11_guard_runs_before_any_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = self._archive(root)
            install = root / "should-not-exist"

            with patch(
                "gate17_clean_windows_install.require_external_windows_11_workstation",
                side_effect=ReleaseReadinessError("Windows 11 required"),
            ):
                with self.assertRaisesRegex(ReleaseReadinessError, "Windows 11"):
                    run_clean_windows_install_receipt(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        install_root=install,
                        output_dir=root / "receipts",
                        repo_root=repo,
                    )

            self.assertFalse(install.exists())

    def test_existing_install_directory_and_existing_receipt_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = self._archive(root)

            install = root / "occupied-install"
            install.mkdir()
            with patch(
                "gate17_clean_windows_install.require_external_windows_11_workstation",
                return_value={"platform": "Windows-11", "windows_build": 26200},
            ):
                with self.assertRaisesRegex(
                    CleanWindowsInstallReceiptError,
                    "must not already exist",
                ):
                    run_clean_windows_install_receipt(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        install_root=install,
                        output_dir=root / "receipts-a",
                        repo_root=repo,
                    )

            receipt_dir = root / "receipts-b"
            receipt_dir.mkdir()
            (receipt_dir / "clean_windows_install.json").write_text(
                "{}",
                encoding="utf-8",
            )
            fresh_install = root / "fresh-install"
            with patch(
                "gate17_clean_windows_install.require_external_windows_11_workstation",
                return_value={"platform": "Windows-11", "windows_build": 26200},
            ):
                with self.assertRaisesRegex(
                    CleanWindowsInstallReceiptError,
                    "do not overwrite",
                ):
                    run_clean_windows_install_receipt(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        install_root=fresh_install,
                        output_dir=receipt_dir,
                        repo_root=repo,
                    )
            self.assertFalse(fresh_install.exists())

    def test_manifest_checksum_mismatch_blocks_smoke_and_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = self._archive(root, bad_hash=True)

            with (
                patch(
                    "gate17_clean_windows_install.require_external_windows_11_workstation",
                    return_value={"platform": "Windows-11", "windows_build": 26200},
                ),
                patch("gate17_clean_windows_install.subprocess.run") as runner,
            ):
                with self.assertRaisesRegex(
                    CleanWindowsInstallReceiptError,
                    "checksum mismatch",
                ):
                    run_clean_windows_install_receipt(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        install_root=root / "install",
                        output_dir=root / "receipts",
                        repo_root=repo,
                    )
            runner.assert_not_called()
            self.assertFalse((root / "receipts" / "clean_windows_install.json").exists())

    def test_archive_traversal_and_windows_case_collision_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            traversal = root / "traversal.zip"
            with zipfile.ZipFile(traversal, "w") as zf:
                zf.writestr("package/../escape.txt", b"x")
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "unsafe path",
            ):
                _preflight_archive(traversal)

            collision = root / "collision.zip"
            with zipfile.ZipFile(collision, "w") as zf:
                zf.writestr("package/File.txt", b"a")
                zf.writestr("package/file.TXT", b"b")
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "Windows path collision",
            ):
                _preflight_archive(collision)

    def test_windows_reserved_and_ads_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            reserved = root / "reserved.zip"
            with zipfile.ZipFile(reserved, "w") as zf:
                zf.writestr("package/CON.txt", b"x")
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "reserved Windows path",
            ):
                _preflight_archive(reserved)

            ads = root / "ads.zip"
            with zipfile.ZipFile(ads, "w") as zf:
                zf.writestr("package/file.txt:stream", b"x")
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "unsafe Windows path",
            ):
                _preflight_archive(ads)

    def test_receipt_directory_must_be_disjoint_from_install_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = self._archive(root)
            install = root / "install"

            with patch(
                "gate17_clean_windows_install.require_external_windows_11_workstation",
                return_value={"platform": "Windows-11", "windows_build": 26200},
            ):
                with self.assertRaisesRegex(
                    CleanWindowsInstallReceiptError,
                    "disjoint",
                ):
                    run_clean_windows_install_receipt(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        install_root=install,
                        output_dir=install / "receipts",
                        repo_root=repo,
                    )
            self.assertFalse(install.exists())

    def test_installed_payload_rejects_unexpected_file(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            (package / "a.bin").write_bytes(b"a")
            (package / "extra.bin").write_bytes(b"x")
            manifest = {
                "files": [
                    {
                        "path": "a.bin",
                        "size_bytes": 1,
                        "sha256": digest(b"a"),
                    }
                ]
            }
            with self.assertRaisesRegex(
                CleanWindowsInstallReceiptError,
                "extra=",
            ):
                validate_installed_payload(package, manifest)


if __name__ == "__main__":
    unittest.main()
