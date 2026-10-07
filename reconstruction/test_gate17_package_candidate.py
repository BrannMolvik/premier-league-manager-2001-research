import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from gate17_package_candidate import (
    PackageCandidateError,
    REQUIRED_BUNDLED_FILES,
    REQUIRED_EXACT_BUNDLED_SHA256,
    build_release_candidate,
    validate_distribution,
)


COMMIT = "a" * 40


class Gate17PackageCandidateTests(unittest.TestCase):
    def _distribution(self, root: Path) -> Path:
        dist = root / "dist"
        (dist / "original_assets").mkdir(parents=True)
        (dist / "FM2001-Windows11.exe").write_bytes(b"fake-exe")
        for relative in REQUIRED_BUNDLED_FILES:
            path = dist / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            # Bundle the real source font so distribution tests exercise the
            # same exact-byte guard used in an actual packaged build.
            if relative in REQUIRED_EXACT_BUNDLED_SHA256:
                original = Path(__file__).resolve().parent.parent / relative
                path.write_bytes(original.read_bytes())
            else:
                path.write_bytes(("asset:" + relative).encode("utf-8"))
        (dist / "runtime.bin").write_bytes(b"runtime")
        return dist

    def test_distribution_accepts_pyinstaller_v6_internal_data_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dist = self._distribution(root)
            internal = dist / "_internal"
            internal.mkdir()
            (dist / "original_assets").rename(internal / "original_assets")

            files = validate_distribution(dist, "FM2001-Windows11.exe")

            self.assertTrue(files)
            self.assertTrue(
                (internal / "original_assets" / "MANIFEST.md").is_file()
            )

    def test_source_club_name_font_must_be_present_and_byte_identical(self):
        relative = "original_assets/source/Fonts/Zurich_BdXCn_BT_36pixel.fnt"
        self.assertIn(relative, REQUIRED_BUNDLED_FILES)
        self.assertEqual(
            REQUIRED_EXACT_BUNDLED_SHA256[relative],
            "92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df",
        )
        with tempfile.TemporaryDirectory() as temp:
            dist = self._distribution(Path(temp))
            staged = dist / relative
            self.assertEqual(len(staged.read_bytes()), 155_544)
            self.assertTrue(validate_distribution(dist, "FM2001-Windows11.exe"))

            original = staged.read_bytes()
            staged.unlink()
            with self.assertRaisesRegex(PackageCandidateError, "must resolve exactly once"):
                validate_distribution(dist, "FM2001-Windows11.exe")

            changed = bytearray(original)
            changed[-1] ^= 1
            staged.write_bytes(changed)
            with self.assertRaisesRegex(PackageCandidateError, "checksum mismatch"):
                validate_distribution(dist, "FM2001-Windows11.exe")

    def test_distribution_rejects_user_owned_game_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dist = self._distribution(root)
            (dist / "Master.dat").write_bytes(b"must-not-ship")
            with self.assertRaisesRegex(
                PackageCandidateError,
                "must not redistribute",
            ):
                validate_distribution(dist, "FM2001-Windows11.exe")

    def test_candidate_archive_is_deterministic_and_identity_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            dist = self._distribution(root)
            first = root / "out-a"
            second = root / "out-b"

            result_a = build_release_candidate(
                dist_root=dist,
                output_dir=first,
                repo_root=repo,
                release_version="rc-test",
                repository_commit=COMMIT,
            )
            result_b = build_release_candidate(
                dist_root=dist,
                output_dir=second,
                repo_root=repo,
                release_version="rc-test",
                repository_commit=COMMIT,
            )

            self.assertEqual(result_a["archive_sha256"], result_b["archive_sha256"])
            self.assertEqual(result_a["archive_size_bytes"], result_b["archive_size_bytes"])
            sidecar = json.loads(Path(result_a["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(sidecar["repository_commit"], COMMIT)
            self.assertFalse(sidecar["external_original_game_data_bundled"])
            self.assertTrue(sidecar["external_game_data_required_at_runtime"])

            with zipfile.ZipFile(result_a["archive"]) as archive:
                names = tuple(archive.namelist())
                self.assertTrue(any(name.endswith("/PACKAGE-MANIFEST.json") for name in names))
                self.assertTrue(any(name.endswith("/README-RELEASE.txt") for name in names))
                self.assertFalse(any(name.casefold().endswith("/master.dat") for name in names))

    def test_output_must_be_outside_repo_and_empty(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            dist = self._distribution(root)
            with self.assertRaisesRegex(PackageCandidateError, "outside"):
                build_release_candidate(
                    dist_root=dist,
                    output_dir=repo / "release",
                    repo_root=repo,
                    release_version="rc",
                    repository_commit=COMMIT,
                )

            out = root / "occupied"
            out.mkdir()
            (out / "old.txt").write_text("stale", encoding="utf-8")
            with self.assertRaisesRegex(PackageCandidateError, "empty"):
                build_release_candidate(
                    dist_root=dist,
                    output_dir=out,
                    repo_root=repo,
                    release_version="rc",
                    repository_commit=COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
