from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bundled_startup_media import (
    BUNDLED_STARTUP_MEDIA_DIRECTORY,
    BUNDLED_STARTUP_MEDIA_MANIFEST,
    BUNDLED_STARTUP_MEDIA_SPECS,
    BundledStartupMediaError,
    bundled_startup_media_contract,
    expected_bundled_startup_media_manifest,
    load_bundled_startup_media_derivatives,
)
from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE


class BundledStartupMediaTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        media = root / BUNDLED_STARTUP_MEDIA_DIRECTORY
        media.mkdir(parents=True)
        manifest = expected_bundled_startup_media_manifest()
        (root / BUNDLED_STARTUP_MEDIA_MANIFEST).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for item in BUNDLED_STARTUP_MEDIA_SPECS:
            path = media / item.filename
            with path.open("wb") as handle:
                handle.truncate(item.size_bytes)
        return temp, root

    def test_exact_manifest_and_hashes_load_source_ordered_derivatives(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        digest_by_name = {
            item.filename: item.sha256
            for item in BUNDLED_STARTUP_MEDIA_SPECS
        }
        with patch(
            "bundled_startup_media._sha256_file",
            side_effect=lambda path: digest_by_name[path.name],
        ):
            items = load_bundled_startup_media_derivatives(root)

        self.assertEqual(
            tuple(item.spec for item in items),
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
        )
        self.assertEqual(
            tuple(item.sequence for item in items),
            (0, 1),
        )
        self.assertEqual(
            tuple(item.path.name for item in items),
            ("easp.mp4", "premintro.mp4"),
        )
        self.assertEqual(
            tuple(item.converted_sha256 for item in items),
            tuple(item.sha256 for item in BUNDLED_STARTUP_MEDIA_SPECS),
        )

    def test_manifest_drift_fails_before_derivative_hashing(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        manifest_path = root / BUNDLED_STARTUP_MEDIA_MANIFEST
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["outputs"][0]["converted_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(payload), encoding="utf-8")

        with patch("bundled_startup_media._sha256_file") as digest:
            with self.assertRaisesRegex(BundledStartupMediaError, "manifest differs"):
                load_bundled_startup_media_derivatives(root)
        digest.assert_not_called()

    def test_missing_size_or_hash_drift_fails_closed(self):
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        first = BUNDLED_STARTUP_MEDIA_SPECS[0]
        first_path = root / BUNDLED_STARTUP_MEDIA_DIRECTORY / first.filename

        first_path.unlink()
        with self.assertRaisesRegex(BundledStartupMediaError, "unavailable"):
            load_bundled_startup_media_derivatives(root)

        with first_path.open("wb") as handle:
            handle.truncate(first.size_bytes - 1)
        with self.assertRaisesRegex(BundledStartupMediaError, "size mismatch"):
            load_bundled_startup_media_derivatives(root)

        with first_path.open("wb") as handle:
            handle.truncate(first.size_bytes)
        with patch(
            "bundled_startup_media._sha256_file",
            return_value="f" * 64,
        ):
            with self.assertRaisesRegex(BundledStartupMediaError, "checksum mismatch"):
                load_bundled_startup_media_derivatives(root)

    def test_contract_keeps_windows_and_gate_completion_false(self):
        contract = bundled_startup_media_contract()
        self.assertTrue(contract["default_package_derivatives_verified"])
        self.assertFalse(contract["windows_playback_verified"])
        self.assertFalse(contract["skip_input_recovered"])
        self.assertFalse(contract["transition_timing_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_expected_manifest_is_exact_two_item_source_contract(self):
        payload = expected_bundled_startup_media_manifest()
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(
            tuple(item["source_path"] for item in payload["outputs"]),
            tuple(item.source_path for item in ORIGINAL_STARTUP_MEDIA_SEQUENCE),
        )
        self.assertEqual(
            tuple(item["converted_size_bytes"] for item in payload["outputs"]),
            (289_307, 6_929_242),
        )
        self.assertFalse(payload["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
