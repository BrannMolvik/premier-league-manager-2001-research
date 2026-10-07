"""Tests for Gate-17 GNU ld archive-member/direct-object evidence."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_link_map_audit import LinkMapAuditError, audit_link_maps


RELEASE_LOG = """gcc -static -o ffmpeg_g.exe ffmpeg.o D:/msys64/ucrt64/lib/libfoo.a -lm
gcc -static -o ffprobe_g.exe ffprobe.o D:/msys64/ucrt64/lib/libfoo.a -lm
"""
FFMPEG_MAP_LOG = """gcc -static -Wl,-Map,ffmpeg-link.map -o ffmpeg_g.exe ffmpeg.o D:/msys64/ucrt64/lib/libfoo.a -lm
"""
FFPROBE_MAP_LOG = """gcc -static -Wl,-Map,ffprobe-link.map -o ffprobe_g.exe ffprobe.o D:/msys64/ucrt64/lib/libfoo.a -lm
"""
FFMPEG_MAP = """Archive member included to satisfy reference by file (symbol)

D:/msys64/ucrt64/lib/libfoo.a(foo.o)
                              ffmpeg.o (foo)

Discarded input sections
 .text          0x0 0x0 ffmpeg.o

Linker script and memory map
LOAD ffmpeg.o
LOAD D:/msys64/ucrt64/lib/crt2.o
LOAD D:/msys64/ucrt64/lib/libfoo.a
"""
FFPROBE_MAP = """Archive member included to satisfy reference by file (symbol)

D:/msys64/ucrt64/lib/libfoo.a(foo.o)
                              ffprobe.o (foo)

Linker script and memory map
LOAD ffprobe.o
LOAD D:/msys64/ucrt64/lib/crt2.o
LOAD D:/msys64/ucrt64/lib/libfoo.a
"""
OWNERSHIP = {
    "passed": True,
    "package_lock_ownership_validated": True,
    "critical_source_family_mapping_validated": True,
    "targets": {
        "ffmpeg_g.exe": {
            "inputs": [
                {
                    "trace_path": "D:/msys64/ucrt64/lib/libfoo.a",
                    "normalized_path": "/ucrt64/lib/libfoo.a",
                    "package": "toolchain-crt",
                    "version": "1.0",
                    "source_family": "crt-source",
                },
                {
                    "trace_path": "D:/msys64/ucrt64/lib/libunused.a",
                    "normalized_path": "/ucrt64/lib/libunused.a",
                    "package": "toolchain-crt",
                    "version": "1.0",
                    "source_family": "crt-source",
                },
                {
                    "trace_path": "D:/msys64/ucrt64/lib/crt2.o",
                    "normalized_path": "/ucrt64/lib/crt2.o",
                    "package": "toolchain-crt",
                    "version": "1.0",
                    "source_family": "crt-source",
                },
            ]
        },
        "ffprobe_g.exe": {
            "inputs": [
                {
                    "trace_path": "D:/msys64/ucrt64/lib/libfoo.a",
                    "normalized_path": "/ucrt64/lib/libfoo.a",
                    "package": "toolchain-crt",
                    "version": "1.0",
                    "source_family": "crt-source",
                },
                {
                    "trace_path": "D:/msys64/ucrt64/lib/crt2.o",
                    "normalized_path": "/ucrt64/lib/crt2.o",
                    "package": "toolchain-crt",
                    "version": "1.0",
                    "source_family": "crt-source",
                },
            ]
        },
    },
}


class Gate17FfmpegLinkMapAuditTests(unittest.TestCase):
    def run_audit(
        self,
        *,
        release_log=RELEASE_LOG,
        ffmpeg_map_log=FFMPEG_MAP_LOG,
        ffprobe_map_log=FFPROBE_MAP_LOG,
        ffmpeg_map=FFMPEG_MAP,
        ffprobe_map=FFPROBE_MAP,
        ownership=OWNERSHIP,
        mapped_ffmpeg=b"same-ffmpeg",
        mapped_ffprobe=b"same-ffprobe",
    ):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {
                "release.log": release_log,
                "ffmpeg-map-build.log": ffmpeg_map_log,
                "ffprobe-map-build.log": ffprobe_map_log,
                "ffmpeg.map": ffmpeg_map,
                "ffprobe.map": ffprobe_map,
            }
            for name, value in paths.items():
                (root / name).write_text(value, encoding="utf-8")
            (root / "ownership.json").write_text(
                json.dumps(ownership), encoding="utf-8"
            )
            (root / "release-ffmpeg.exe").write_bytes(b"same-ffmpeg")
            (root / "release-ffprobe.exe").write_bytes(b"same-ffprobe")
            (root / "mapped-ffmpeg.exe").write_bytes(mapped_ffmpeg)
            (root / "mapped-ffprobe.exe").write_bytes(mapped_ffprobe)
            return audit_link_maps(
                release_build_log=root / "release.log",
                ffmpeg_map_build_log=root / "ffmpeg-map-build.log",
                ffprobe_map_build_log=root / "ffprobe-map-build.log",
                ffmpeg_map=root / "ffmpeg.map",
                ffprobe_map=root / "ffprobe.map",
                ownership_proof=root / "ownership.json",
                release_ffmpeg_unstripped=root / "release-ffmpeg.exe",
                release_ffprobe_unstripped=root / "release-ffprobe.exe",
                mapped_ffmpeg_unstripped=root / "mapped-ffmpeg.exe",
                mapped_ffprobe_unstripped=root / "mapped-ffprobe.exe",
            )

    def test_member_and_direct_object_proof_stays_bounded(self):
        result = self.run_audit()
        self.assertTrue(result["passed"])
        ffmpeg = result["targets"]["ffmpeg_g.exe"]
        self.assertTrue(ffmpeg["unstripped_binary_byte_identical"])
        self.assertEqual(ffmpeg["traced_external_archive_count"], 2)
        self.assertEqual(ffmpeg["contributing_external_archive_count"], 1)
        self.assertEqual(
            ffmpeg["traced_but_noncontributing_external_archives"],
            ["D:/msys64/ucrt64/lib/libunused.a"],
        )
        self.assertEqual(
            ffmpeg["contributing_external_archives"][0]["members"], ["foo.o"]
        )
        self.assertEqual(ffmpeg["direct_external_object_count"], 1)
        self.assertTrue(result["archive_member_contribution_proof_complete"])
        self.assertTrue(result["direct_object_contribution_proof_complete"])
        self.assertFalse(result["static_contributor_attribution_complete"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_unknown_external_archive_member_fails_closed(self):
        polluted = FFMPEG_MAP.replace(
            "D:/msys64/ucrt64/lib/libfoo.a(foo.o)",
            "D:/msys64/ucrt64/lib/libother.a(other.o)",
        )
        with self.assertRaisesRegex(LinkMapAuditError, "unowned external archive"):
            self.run_audit(ffmpeg_map=polluted)

    def test_missing_direct_object_load_fails_closed(self):
        missing = FFMPEG_MAP.replace(
            "LOAD D:/msys64/ucrt64/lib/crt2.o\n", ""
        )
        with self.assertRaisesRegex(LinkMapAuditError, "direct-object coverage mismatch"):
            self.run_audit(ffmpeg_map=missing)

    def test_map_command_drift_beyond_observation_flag_fails_closed(self):
        drifted = FFMPEG_MAP_LOG.replace(" -lm", " -lws2_32")
        with self.assertRaisesRegex(LinkMapAuditError, "drifted"):
            self.run_audit(ffmpeg_map_log=drifted)

    def test_missing_or_duplicate_map_flag_fails_closed(self):
        with self.assertRaisesRegex(LinkMapAuditError, "exactly one"):
            self.run_audit(
                ffmpeg_map_log=FFMPEG_MAP_LOG.replace(
                    " -Wl,-Map,ffmpeg-link.map", ""
                )
            )

    def test_map_relink_byte_drift_fails_closed(self):
        with self.assertRaisesRegex(LinkMapAuditError, "differs"):
            self.run_audit(mapped_ffmpeg=b"different")

    def test_missing_archive_inclusion_section_fails_closed(self):
        with self.assertRaisesRegex(LinkMapAuditError, "inclusion section"):
            self.run_audit(
                ffmpeg_map=FFMPEG_MAP.replace(
                    "Archive member included to satisfy reference by file (symbol)",
                    "Different heading",
                )
            )

    def test_unvalidated_ownership_proof_fails_closed(self):
        ownership = json.loads(json.dumps(OWNERSHIP))
        ownership["package_lock_ownership_validated"] = False
        with self.assertRaisesRegex(LinkMapAuditError, "package lock"):
            self.run_audit(ownership=ownership)

    def test_workflow_pins_pe_timestamp_to_pinned_source_epoch(self):
        repo = Path(__file__).resolve().parent.parent
        workflow = (
            repo / ".github" / "workflows" / "gate17-minimal-ffmpeg-build.yml"
        ).read_text(encoding="utf-8")
        start = workflow.index(
            "      - name: Build exact minimal FFmpeg helper and capture link evidence"
        )
        end = workflow.index(
            "      - name: Audit resolved final-link inputs", start
        )
        step = workflow[start:end]
        self.assertIn(
            'SOURCE_DATE_EPOCH="$(git show -s --format=%ct HEAD)"', step
        )
        self.assertIn("export SOURCE_DATE_EPOCH", step)
        self.assertIn("Pinned SOURCE_DATE_EPOCH:", step)
        self.assertNotIn("--no-insert-timestamp", step)

    def test_workflow_keeps_release_unstripped_binaries_out_of_artifact(self):
        repo = Path(__file__).resolve().parent.parent
        workflow = (
            repo / ".github" / "workflows" / "gate17-minimal-ffmpeg-build.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'cp ffmpeg_g.exe "$OUT/release-unstripped/ffmpeg_g.exe"', workflow
        )
        self.assertIn(
            'cp ffprobe_g.exe "$OUT/release-unstripped/ffprobe_g.exe"', workflow
        )
        self.assertIn("link-member-proof.json", workflow)
        upload = workflow[workflow.index("      - name: Upload exact minimal build proof"):]
        self.assertNotIn(
            "_minimal-ffmpeg-build/release-unstripped/ffmpeg_g.exe", upload
        )
        self.assertNotIn(
            "_minimal-ffmpeg-build/release-unstripped/ffprobe_g.exe", upload
        )


if __name__ == "__main__":
    unittest.main()
