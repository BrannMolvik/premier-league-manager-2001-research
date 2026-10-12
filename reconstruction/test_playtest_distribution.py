"""Focused tests for the separate nonfinal direct-layout diagnostic artifact."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from playtest_distribution import (
    PlaytestDistributionError, prepare_playtest_distribution,
)

COMMIT = "abcdef0123456789abcdef0123456789abcdef01"


class PlaytestDistributionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "dist" / "FM2001-Windows11"
        (self.root / "_internal").mkdir(parents=True)
        (self.root / "_internal" / "runtime.txt").write_text("frozen", encoding="utf-8")
        (self.root / "FM2001-Windows11.exe").write_bytes(b"MZfake-test-exe")

    def test_valid_tree_annotates_without_touching_program(self):
        before = (self.root / "FM2001-Windows11.exe").read_bytes()
        receipt = prepare_playtest_distribution(self.root, COMMIT)
        self.assertEqual(receipt["repository_commit"], COMMIT)
        self.assertEqual(receipt["executable_sha256"], hashlib.sha256(before).hexdigest())
        self.assertFalse(receipt["windows11_interactive_acceptance_verified"])
        self.assertTrue(receipt["external_original_game_data_required"])
        self.assertFalse(receipt["original_executable_bundled"])
        self.assertEqual((self.root / "FM2001-Windows11.exe").read_bytes(), before)
        self.assertEqual(json.loads((self.root / "PLAYTEST-RECEIPT.json").read_text()), receipt)
        self.assertIn("not an approved release", (self.root / "PLAYTEST-README.txt").read_text())
        self.assertFalse((self.root / "footballmanager.exe").exists())
        self.assertFalse((self.root / "FM2001").exists())

    def test_idempotent_same_exact_head_and_no_nesting(self):
        a = prepare_playtest_distribution(self.root, COMMIT)
        b = prepare_playtest_distribution(str(self.root), COMMIT)
        self.assertEqual(a, b)
        self.assertEqual(len(list(self.root.glob("*.zip"))), 0)

    def test_requires_real_frozen_exe_and_internal(self):
        for path in (self.root / "FM2001-Windows11.exe", self.root / "_internal"):
            with self.subTest(path=path):
                backup = path.with_name(path.name + ".bak")
                path.rename(backup)
                try:
                    with self.assertRaises(PlaytestDistributionError):
                        prepare_playtest_distribution(self.root, COMMIT)
                finally:
                    backup.rename(path)
        (self.root / "_internal" / "runtime.txt").unlink()
        with self.assertRaises(PlaytestDistributionError):
            prepare_playtest_distribution(self.root, COMMIT)

    def test_cannot_bundle_original_install_or_nested_zip(self):
        for name in ("footballmanager.exe", "FM2001", "inner.zip"):
            path = self.root / name
            if name == "FM2001":
                path.mkdir()
            else:
                path.write_bytes(b"private-game-data-never-allowed")
            try:
                with self.subTest(name=name), self.assertRaises(PlaytestDistributionError):
                    prepare_playtest_distribution(self.root, COMMIT)
            finally:
                path.rmdir() if path.is_dir() else path.unlink()

    def test_bad_commit_fails_without_writing_files(self):
        for val in ("A"*40, "a"*39, "a"*41, None, True, "../evil"):
            with self.subTest(val=val), self.assertRaises(PlaytestDistributionError):
                prepare_playtest_distribution(self.root, val)
        self.assertFalse((self.root / "PLAYTEST-RECEIPT.json").exists())


if __name__ == "__main__":
    unittest.main()
