"""Tests for the Gate-17 static-contributor source bundle contract."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate17_source_material_bundle import (
    CONTRACT_PATH,
    SourceBundleError,
    audit_source_bundle_contract,
    materialize_source_bundle,
)


class Gate17SourceMaterialBundleTests(unittest.TestCase):
    def real_contract(self) -> dict:
        root = Path(__file__).resolve().parents[1]
        return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))

    def write_contract(self, temp: str, payload: dict) -> Path:
        root = Path(temp)
        path = root / CONTRACT_PATH
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return root

    def test_real_contract_resolves_exact_four_contributor_families(self):
        root = Path(__file__).resolve().parents[1]
        result = audit_source_bundle_contract(root)
        self.assertTrue(result["passed"])
        self.assertEqual(result["bundle_scope_count"], 4)
        self.assertEqual(
            [item["source_family"] for item in result["entries"]],
            [
                "mingw-w64-crt",
                "mingw-w64-gcc",
                "mingw-w64-winpthreads",
                "mingw-w64-windows-default-manifest",
            ],
        )
        self.assertFalse(result["source_package_bundle_assembled"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_unverified_source_family_fails_closed(self):
        payload = self.real_contract()
        payload["critical_package_source_material"]["source_families"][
            "mingw-w64-gcc"
        ]["source_tarball_metadata_verified"] = False
        with tempfile.TemporaryDirectory() as temp:
            root = self.write_contract(temp, payload)
            with self.assertRaisesRegex(SourceBundleError, "not verified"):
                audit_source_bundle_contract(root)

    def test_non_msys2_source_url_fails_closed(self):
        payload = self.real_contract()
        payload["critical_package_source_material"]["source_families"][
            "mingw-w64-crt"
        ]["source_only_tarball"] = "https://example.com/crt.src.tar.zst"
        with tempfile.TemporaryDirectory() as temp:
            root = self.write_contract(temp, payload)
            with self.assertRaisesRegex(SourceBundleError, "outside"):
                audit_source_bundle_contract(root)

    def test_family_order_must_match_package_mapping_exactly(self):
        payload = self.real_contract()
        payload["static_contributor_source_material"][
            "contributing_source_families"
        ] = list(
            reversed(
                payload["static_contributor_source_material"][
                    "contributing_source_families"
                ]
            )
        )
        with tempfile.TemporaryDirectory() as temp:
            root = self.write_contract(temp, payload)
            with self.assertRaisesRegex(SourceBundleError, "exactly match"):
                audit_source_bundle_contract(root)

    def test_materialization_hashes_downloaded_bytes_without_promoting_completion(self):
        payload = self.real_contract()
        with tempfile.TemporaryDirectory() as temp:
            root = self.write_contract(temp, payload)
            output = Path(temp) / "out"

            expected = {
                item["source_url"]: (
                    item["expected_sha256"],
                    item["expected_size_bytes"],
                )
                for item in audit_source_bundle_contract(root)["entries"]
            }

            def fake_download(url, destination):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"synthetic")
                return expected[url]

            with patch(
                "gate17_source_material_bundle._download",
                side_effect=fake_download,
            ):
                result = materialize_source_bundle(
                    repo_root=root,
                    output_dir=output,
                )

            self.assertTrue(result["source_package_bundle_assembled"])
            self.assertEqual(result["source_package_count"], 4)
            self.assertFalse(result["source_package_hashes_pinned"])
            self.assertFalse(result["license_notice_material_complete"])
            self.assertFalse(result["source_material_complete"])
            self.assertFalse(result["legal_compliance_claimed"])
            self.assertTrue((output / "source-package-manifest.json").is_file())
            self.assertEqual(
                len(list((output / "source-packages").glob("*.src.tar.zst"))),
                4,
            )


    def test_download_hash_drift_fails_closed(self):
        payload = self.real_contract()
        with tempfile.TemporaryDirectory() as temp:
            root = self.write_contract(temp, payload)
            output = Path(temp) / "out"
            with patch(
                "gate17_source_material_bundle._download",
                return_value=("0" * 64, 1),
            ):
                with self.assertRaisesRegex(SourceBundleError, "SHA-256 drifted"):
                    materialize_source_bundle(
                        repo_root=root,
                        output_dir=output,
                    )


if __name__ == "__main__":
    unittest.main()
