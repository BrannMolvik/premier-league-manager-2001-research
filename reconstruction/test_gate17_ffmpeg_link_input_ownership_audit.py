"""Tests for direct package ownership of Gate-17 linker inputs."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_link_input_ownership_audit import (
    LinkInputOwnershipError,
    audit_link_input_ownership,
)


FFMPEG_TRACE = """libavutil\\libavutil.a
D:/msys64/ucrt64/lib/libm.a
D:/msys64/ucrt64/lib/libatomic.a
D:/msys64/ucrt64/lib/crt2.o
D:/msys64/ucrt64/lib/libm.a
"""
FFPROBE_TRACE = """libavutil\\libavutil.a
D:/msys64/ucrt64/lib/libm.a
D:/msys64/ucrt64/lib/crt2.o
"""
OWNER_ROWS = """ffmpeg_g.exe\tD:/msys64/ucrt64/lib/crt2.o\t/ucrt64/lib/crt2.o\tmingw-w64-ucrt-x86_64-crt\t14.0-1
ffmpeg_g.exe\tD:/msys64/ucrt64/lib/libatomic.a\t/ucrt64/lib/libatomic.a\tmingw-w64-ucrt-x86_64-libatomic\t16.2-4
ffmpeg_g.exe\tD:/msys64/ucrt64/lib/libm.a\t/ucrt64/lib/libm.a\tmingw-w64-ucrt-x86_64-crt\t14.0-1
ffprobe_g.exe\tD:/msys64/ucrt64/lib/crt2.o\t/ucrt64/lib/crt2.o\tmingw-w64-ucrt-x86_64-crt\t14.0-1
ffprobe_g.exe\tD:/msys64/ucrt64/lib/libm.a\t/ucrt64/lib/libm.a\tmingw-w64-ucrt-x86_64-crt\t14.0-1
"""
LOCK = """mingw-w64-ucrt-x86_64-crt 14.0-1
mingw-w64-ucrt-x86_64-libatomic 16.2-4
"""
CONTRACT = {
    "required_package_versions": {
        "mingw-w64-ucrt-x86_64-crt": "14.0-1",
        "mingw-w64-ucrt-x86_64-libatomic": "16.2-4",
    },
    "critical_package_source_material": {
        "package_to_source_family": {
            "mingw-w64-ucrt-x86_64-crt": "mingw-w64-crt",
            "mingw-w64-ucrt-x86_64-libatomic": "mingw-w64-gcc",
        },
        "source_families": {
            "mingw-w64-crt": {
                "binary_version": "14.0-1",
                "source_tarball_metadata_verified": True,
            },
            "mingw-w64-gcc": {
                "binary_version": "16.2-4",
                "source_tarball_metadata_verified": True,
            },
        },
    },
}


class Gate17LinkInputOwnershipAuditTests(unittest.TestCase):
    def run_audit(
        self,
        *,
        ffmpeg=FFMPEG_TRACE,
        ffprobe=FFPROBE_TRACE,
        owners=OWNER_ROWS,
        lock=LOCK,
        contract=CONTRACT,
    ):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "ffmpeg.log").write_text(ffmpeg, encoding="utf-8")
            (root / "ffprobe.log").write_text(ffprobe, encoding="utf-8")
            (root / "owners.tsv").write_text(owners, encoding="utf-8")
            (root / "lock.txt").write_text(lock, encoding="utf-8")
            (root / "contract.json").write_text(
                json.dumps(contract), encoding="utf-8"
            )
            return audit_link_input_ownership(
                ffmpeg_trace_log=root / "ffmpeg.log",
                ffprobe_trace_log=root / "ffprobe.log",
                owner_rows=root / "owners.tsv",
                package_lock=root / "lock.txt",
                toolchain_contract=root / "contract.json",
            )

    def test_complete_direct_ownership_is_recorded_without_contribution_claim(self):
        result = self.run_audit()
        self.assertTrue(result["passed"])
        self.assertEqual(result["targets"]["ffmpeg_g.exe"]["external_input_count"], 3)
        self.assertEqual(result["targets"]["ffprobe_g.exe"]["external_input_count"], 2)
        self.assertEqual(result["unique_owner_package_count"], 2)
        self.assertTrue(result["package_lock_ownership_validated"])
        self.assertTrue(result["critical_source_family_mapping_validated"])
        self.assertFalse(result["archive_member_contribution_proof_complete"])
        self.assertFalse(result["static_contributor_attribution_complete"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_relative_internal_ffmpeg_inputs_are_excluded(self):
        result = self.run_audit()
        paths = {
            item["trace_path"]
            for item in result["targets"]["ffmpeg_g.exe"]["inputs"]
        }
        self.assertNotIn("libavutil/libavutil.a", paths)

    def test_missing_owner_row_fails_closed(self):
        owners = OWNER_ROWS.replace(
            "ffmpeg_g.exe\tD:/msys64/ucrt64/lib/libatomic.a\t"
            "/ucrt64/lib/libatomic.a\tmingw-w64-ucrt-x86_64-libatomic\t16.2-4\n",
            "",
        )
        with self.assertRaisesRegex(LinkInputOwnershipError, "coverage mismatch"):
            self.run_audit(owners=owners)

    def test_extra_owner_row_fails_closed(self):
        extra = (
            OWNER_ROWS
            + "ffprobe_g.exe\tD:/msys64/ucrt64/lib/libatomic.a\t"
            "/ucrt64/lib/libatomic.a\tmingw-w64-ucrt-x86_64-libatomic\t16.2-4\n"
        )
        with self.assertRaisesRegex(LinkInputOwnershipError, "coverage mismatch"):
            self.run_audit(owners=extra)

    def test_owner_version_drift_from_lock_fails_closed(self):
        owners = OWNER_ROWS.replace(
            "mingw-w64-ucrt-x86_64-libatomic\t16.2-4",
            "mingw-w64-ucrt-x86_64-libatomic\t16.2-5",
        )
        with self.assertRaisesRegex(LinkInputOwnershipError, "locked"):
            self.run_audit(owners=owners)

    def test_unmapped_owner_fails_closed(self):
        contract = json.loads(json.dumps(CONTRACT))
        del contract["critical_package_source_material"]["package_to_source_family"][
            "mingw-w64-ucrt-x86_64-libatomic"
        ]
        with self.assertRaisesRegex(LinkInputOwnershipError, "no critical source-family"):
            self.run_audit(contract=contract)

    def test_unverified_source_family_fails_closed(self):
        contract = json.loads(json.dumps(CONTRACT))
        contract["critical_package_source_material"]["source_families"][
            "mingw-w64-gcc"
        ]["source_tarball_metadata_verified"] = False
        with self.assertRaisesRegex(LinkInputOwnershipError, "not verified"):
            self.run_audit(contract=contract)


if __name__ == "__main__":
    unittest.main()
