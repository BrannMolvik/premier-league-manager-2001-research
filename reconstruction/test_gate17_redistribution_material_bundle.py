"""Tests for the integrated Gate-17 redistribution-material bundle."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate17_redistribution_material_bundle import (
    assemble_redistribution_material_bundle,
    audit_redistribution_material_contract,
)
from gate17_source_material_bundle import CONTRACT_PATH


class Gate17RedistributionMaterialBundleTests(unittest.TestCase):
    def test_real_contract_requires_all_three_pinned_material_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        result = audit_redistribution_material_contract(root)
        self.assertTrue(result["passed"])
        self.assertEqual(result["toolchain_source_family_count"], 4)
        self.assertEqual(result["toolchain_license_evidence_file_count"], 9)
        self.assertTrue(result["ffmpeg_source_snapshot_assembled"])
        self.assertFalse(result["redistribution_material_bundle_assembled"])
        self.assertFalse(result["license_notice_material_complete"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_toolchain_self_promotion_fails_closed(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
        payload["static_contributor_source_material"]["source_material_complete"] = True
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            contract = temp_root / CONTRACT_PATH
            contract.parent.mkdir(parents=True)
            contract.write_text(json.dumps(payload), encoding="utf-8")
            source_contract = (
                root / "third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json"
            )
            target = (
                temp_root
                / "third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json"
            )
            target.write_bytes(source_contract.read_bytes())
            with self.assertRaises(Exception):
                audit_redistribution_material_contract(temp_root)

    def test_mocked_assembly_hashes_full_integrated_file_inventory(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "bundle"

            def fake_sources(*, repo_root, output_dir):
                out = Path(output_dir)
                (out / "source-packages").mkdir(parents=True)
                for index in range(4):
                    (out / "source-packages" / f"source-{index}.src.tar.zst").write_bytes(
                        f"source-{index}".encode()
                    )
                (out / "source-package-manifest.json").write_text("{}\n")
                return {"source_package_count": 4}

            def fake_licenses(*, repo_root, source_packages_dir, output_dir):
                out = Path(output_dir)
                out.mkdir(parents=True)
                for index in range(9):
                    (out / f"license-{index}.txt").write_text(f"license-{index}\n")
                (out / "license-material-manifest.json").write_text("{}\n")
                return {"evidence_file_count": 9}

            def fake_ffmpeg(*, repo_root, ffmpeg_source, output_dir):
                out = Path(output_dir)
                out.mkdir(parents=True)
                (out / "ffmpeg-source.tar.xz").write_bytes(b"ffmpeg")
                (out / "COPYING.LGPLv2.1").write_text("license\n")
                (out / "build-recipe-manifest.json").write_text("{}\n")
                (out / "ffmpeg-source-snapshot-manifest.json").write_text("{}\n")
                return {"assembled": True}

            with (
                patch(
                    "gate17_redistribution_material_bundle.materialize_source_bundle",
                    side_effect=fake_sources,
                ),
                patch(
                    "gate17_redistribution_material_bundle.extract_license_material",
                    side_effect=fake_licenses,
                ),
                patch(
                    "gate17_redistribution_material_bundle.build_snapshot",
                    side_effect=fake_ffmpeg,
                ),
            ):
                result = assemble_redistribution_material_bundle(
                    repo_root=root,
                    ffmpeg_source=Path(temp) / "ffmpeg-source",
                    output_dir=output,
                )

            self.assertTrue(result["redistribution_material_bundle_assembled"])
            self.assertFalse(result["source_material_complete"])
            self.assertFalse(result["legal_compliance_claimed"])
            self.assertTrue((output / "THIRD-PARTY-MATERIALS.txt").is_file())
            manifest = output / "redistribution-material-manifest.json"
            self.assertTrue(manifest.is_file())
            payload = json.loads(manifest.read_text())
            self.assertEqual(payload["file_count"], len(payload["files"]))
            self.assertTrue(all(len(row["sha256"]) == 64 for row in payload["files"]))
            self.assertNotIn(
                "redistribution-material-manifest.json",
                {row["path"] for row in payload["files"]},
            )


if __name__ == "__main__":
    unittest.main()
