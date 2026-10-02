import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import zipfile

from gate17_windows_package import (
    APP_NAME,
    PYINSTALLER_VERSION,
    ReleasePackageManifest,
    WindowsPackageError,
    create_deterministic_zip,
    require_output_directory_outside_repo,
    require_pyinstaller_version,
    require_windows_build_host,
    validate_package_contents,
    write_external_manifest,
    write_package_build_info,
    write_release_readme,
)


COMMIT = "a" * 40


def synthetic_package(root: Path) -> Path:
    package = root / APP_NAME
    internal = package / "_internal" / "original_assets"
    internal.mkdir(parents=True)
    (package / f"{APP_NAME}.exe").write_bytes(b"MZsynthetic")
    (internal / "MANIFEST.md").write_text("# manifest\n", encoding="utf-8")
    (internal / "source.dat").write_bytes(b"asset")
    return package


class Gate17WindowsPackageTests(unittest.TestCase):
    def test_windows_server_is_allowed_as_build_host_only(self):
        with (
            patch("gate17_windows_package.platform.system", return_value="Windows"),
            patch(
                "gate17_windows_package.platform.platform",
                return_value="Windows-Server-2025",
            ),
        ):
            result = require_windows_build_host()
        self.assertEqual(result["platform"], "Windows-Server-2025")

        with patch("gate17_windows_package.platform.system", return_value="Linux"):
            with self.assertRaisesRegex(
                WindowsPackageError,
                "requires Windows",
            ):
                require_windows_build_host()

    def test_output_directory_must_be_outside_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            with self.assertRaisesRegex(
                WindowsPackageError,
                "outside the Git repository",
            ):
                require_output_directory_outside_repo(repo / "dist", repo)

            outside = require_output_directory_outside_repo(
                Path(temp) / "release",
                repo,
            )
            self.assertTrue(outside.is_dir())

    def test_package_requires_executable_and_provenance_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            package = synthetic_package(Path(temp))
            result = validate_package_contents(package)
            self.assertGreaterEqual(result["file_count"], 3)

            (package / f"{APP_NAME}.exe").unlink()
            with self.assertRaisesRegex(
                WindowsPackageError,
                "packaged executable is missing",
            ):
                validate_package_contents(package)

    def test_package_rejects_original_game_database_and_executable(self):
        for forbidden in ("FOOTBAL.EXE", "Master.dat", "Static.dat"):
            with self.subTest(forbidden=forbidden):
                with tempfile.TemporaryDirectory() as temp:
                    package = synthetic_package(Path(temp))
                    (package / "_internal" / forbidden).write_bytes(b"x")
                    with self.assertRaisesRegex(
                        WindowsPackageError,
                        "original game data/executable",
                    ):
                        validate_package_contents(package)

    def test_package_rejects_raw_disc_image_material(self):
        with tempfile.TemporaryDirectory() as temp:
            package = synthetic_package(Path(temp))
            (package / "_internal" / "original.iso").write_bytes(b"x")
            with self.assertRaisesRegex(
                WindowsPackageError,
                "raw disc-image material",
            ):
                validate_package_contents(package)

    def test_package_build_info_states_original_data_is_external(self):
        with tempfile.TemporaryDirectory() as temp:
            package = synthetic_package(Path(temp))
            path = write_package_build_info(
                package,
                release_version="pr-151",
                repository_commit=COMMIT,
                pyinstaller_version=PYINSTALLER_VERSION,
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["repository_commit"], COMMIT)
            self.assertEqual(payload["release_version"], "pr-151")
            self.assertFalse(payload["original_game_data_bundled"])
            self.assertIn("Master.dat", payload["original_game_data_requirement"])
            self.assertIn("FOOTBAL.EXE", payload["original_game_data_requirement"])

    def test_release_readme_explicitly_excludes_original_game_files(self):
        with tempfile.TemporaryDirectory() as temp:
            package = synthetic_package(Path(temp))
            text = write_release_readme(package).read_text(encoding="utf-8")
            self.assertIn("Master.dat", text)
            self.assertIn("Static.dat", text)
            self.assertIn("FOOTBAL.EXE", text)
            self.assertIn("does NOT include", text)

    def test_zip_archive_is_sorted_fixed_timestamp_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            package = synthetic_package(temp)
            (package / "z-last.txt").write_text("z", encoding="utf-8")
            (package / "a-first.txt").write_text("a", encoding="utf-8")

            first = create_deterministic_zip(package, temp / "first.zip")
            second = create_deterministic_zip(package, temp / "second.zip")

            self.assertEqual(
                sha256(first.read_bytes()).hexdigest(),
                sha256(second.read_bytes()).hexdigest(),
            )
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
                self.assertEqual(names, sorted(names, key=str.lower))
                self.assertTrue(
                    all(info.date_time == (1980, 1, 1, 0, 0, 0)
                        for info in archive.infolist())
                )

    def test_external_manifest_roundtrips_archive_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "release.manifest.json"
            manifest = ReleasePackageManifest(
                schema_version=1,
                release_version="pr-151",
                repository_commit=COMMIT,
                archive_name="release.zip",
                archive_sha256="b" * 64,
                archive_size_bytes=1234,
                app_name=APP_NAME,
                pyinstaller_version=PYINSTALLER_VERSION,
                bundled_original_asset_file_count=63,
            )
            write_external_manifest(target, manifest)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(payload["archive_sha256"], "b" * 64)
            self.assertEqual(payload["archive_size_bytes"], 1234)
            with self.assertRaisesRegex(
                WindowsPackageError,
                "already exists",
            ):
                write_external_manifest(target, manifest)

    def test_pyinstaller_version_is_exactly_pinned(self):
        with patch(
            "gate17_windows_package.importlib.metadata.version",
            return_value=PYINSTALLER_VERSION,
        ):
            self.assertEqual(require_pyinstaller_version(), PYINSTALLER_VERSION)

        with patch(
            "gate17_windows_package.importlib.metadata.version",
            return_value="6.21.0",
        ):
            with self.assertRaisesRegex(
                WindowsPackageError,
                "required, found 6.21.0",
            ):
                require_pyinstaller_version()


if __name__ == "__main__":
    unittest.main()
