"""Tests for the Gate-17 evidence-only final-link trace audit."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_link_trace_audit import LinkTraceAuditError, audit_link_traces


RELEASE = """gcc -static -Wl,--image-base,0x140000000 -o ffmpeg_g.exe ffmpeg.o libavcodec/libavcodec.a -lm
gcc -static -Wl,--image-base,0x140000000 -o ffprobe_g.exe ffprobe.o libavcodec/libavcodec.a -lm
"""
FFMPEG_TRACE = """gcc -static -Wl,--image-base,0x140000000 -Wl,--trace -o ffmpeg_g.exe ffmpeg.o libavcodec/libavcodec.a -lm
libavcodec/libavcodec.a
/ucrt64/lib/libm.a
"""
FFPROBE_TRACE = """gcc -static -Wl,--image-base,0x140000000 -Wl,--trace -o ffprobe_g.exe ffprobe.o libavcodec/libavcodec.a -lm
libavcodec/libavcodec.a
/ucrt64/lib/libm.a
"""


class Gate17FfmpegLinkTraceAuditTests(unittest.TestCase):
    def run_audit(self, release=RELEASE, ffmpeg=FFMPEG_TRACE, ffprobe=FFPROBE_TRACE):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release_path = root / "release.log"
            ffmpeg_path = root / "ffmpeg.log"
            ffprobe_path = root / "ffprobe.log"
            release_path.write_text(release, encoding="utf-8")
            ffmpeg_path.write_text(ffmpeg, encoding="utf-8")
            ffprobe_path.write_text(ffprobe, encoding="utf-8")
            return audit_link_traces(
                release_build_log=release_path,
                ffmpeg_trace_log=ffmpeg_path,
                ffprobe_trace_log=ffprobe_path,
            )

    def test_equivalent_trace_records_resolved_archives_without_completion_claim(self):
        result = self.run_audit()
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["targets"]["ffmpeg_g.exe"]["resolved_archives"],
            ["libavcodec/libavcodec.a", "/ucrt64/lib/libm.a"],
        )
        self.assertTrue(
            result["targets"]["ffprobe_g.exe"][
                "trace_command_matches_release_after_removing_trace_flag"
            ]
        )
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])
        self.assertFalse(result["contributor_package_attribution_complete"])

    def test_trace_command_drift_fails_closed(self):
        drifted = FFMPEG_TRACE.replace("-lm", "-lws2_32")
        with self.assertRaisesRegex(LinkTraceAuditError, "drifted"):
            self.run_audit(ffmpeg=drifted)

    def test_missing_trace_flag_fails_closed(self):
        with self.assertRaisesRegex(LinkTraceAuditError, "exactly one"):
            self.run_audit(ffmpeg=FFMPEG_TRACE.replace(" -Wl,--trace", ""))

    def test_missing_resolved_archive_evidence_fails_closed(self):
        no_archives = (
            "gcc -static -Wl,--image-base,0x140000000 -Wl,--trace "
            "-o ffmpeg_g.exe ffmpeg.o -lm\n"
        )
        with self.assertRaisesRegex(LinkTraceAuditError, "no resolved"):
            self.run_audit(
                release=RELEASE.replace(" libavcodec/libavcodec.a", ""),
                ffmpeg=no_archives,
            )


if __name__ == "__main__":
    unittest.main()
