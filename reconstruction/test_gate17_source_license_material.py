"""Tests for Gate-17 toolchain contributor license-material extraction."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_source_license_material import (
    LicenseMaterialError,
    _verify_bytes,
    audit_license_material_contract,
)
from gate17_source_material_bundle import CONTRACT_PATH


class Gate17SourceLicenseMaterialTests(unittest.TestCase):
    def test_real_contract_pins_four_families_and_nine_evidence_files(self):
        root = Path(__file__).resolve().parents[1]
        result = audit_license_material_contract(root)
        self.assertTrue(result["passed"])
        self.assertEqual(result["source_family_count"], 4)
        self.assertEqual(result["file_count"], 9)
        self.assertTrue(result["license_material_assembled"])
        self.assertTrue(result["license_material_hashes_pinned"])
        self.assertFalse(result["license_notice_material_complete"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_byte_identity_check_fails_closed(self):
        spec = {
            "sha256": "0" * 64,
            "size_bytes": 3,
        }
        with self.assertRaisesRegex(LicenseMaterialError, "SHA-256 drifted"):
            _verify_bytes(b"abc", spec, "synthetic")

    def test_license_completion_cannot_self_promote(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
        payload["static_contributor_source_material"]["license_material"][
            "license_notice_material_complete"
        ] = True
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            path = temp_root / CONTRACT_PATH
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(LicenseMaterialError, "must remain false"):
                audit_license_material_contract(temp_root)

    def test_public_domain_manifest_is_explicitly_not_a_dedicated_license_text(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
        row = payload["static_contributor_source_material"]["license_material"][
            "mingw_w64_windows_default_manifest"
        ]
        self.assertEqual(
            row["evidence_kind"],
            "public_domain_declaration_and_source_evidence",
        )
        self.assertFalse(row["dedicated_license_text_present"])


if __name__ == "__main__":
    unittest.main()
