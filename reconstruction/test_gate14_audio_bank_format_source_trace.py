"""Synthetic tests for the private Gate-14 BNK format tracer."""
from hashlib import sha256
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_audio_bank_format_source_trace import (
    Gate14AudioBankFormatTraceError,
    audio_bank_format_trace_report,
    main as tracer_main,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x600)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x80)
    out[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", out, 0x84, 0x14C, 2)
    struct.pack_into("<H", out, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", out, option, 0x10B)
    struct.pack_into("<I", out, option + 28, 0x400000)
    sections = option + 0xE0

    out[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", out, sections + 8, 0x180, 0x1000, 0x180, 0x200)
    second = sections + 40
    out[second:second + 8] = b".rdata\x00\x00"
    struct.pack_into("<IIII", out, second + 8, 0x100, 0x2000, 0x100, 0x400)
    out[0x210:0x218] = b"\x55\x8b\xec\x90\x90\x90\x5d\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14AudioBankFormatTraceTests(unittest.TestCase):
    def test_collects_bounded_loader_window_without_format_promotion(self):
        pe = parse_fixture()
        report = audio_bank_format_trace_report(
            pe,
            windows=(("synthetic loader", 0x401010, 8),),
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 1)
        self.assertEqual(report["windows"][0]["section"], ".text")
        self.assertEqual(report["windows"][0]["actual_window_bytes"], 8)
        self.assertTrue(report["windows"][0]["linear_disassembly_only"])
        self.assertTrue(report["bank_ownership_recovered"])
        self.assertTrue(report["playback_entrypoints_recovered"])
        for key in (
            "bank_header_layout_recovered",
            "sample_table_layout_recovered",
            "sample_offsets_recovered",
            "sample_codec_recovered",
            "sample_rate_channels_recovered",
            "sample_names_recovered",
            "modern_sample_decode_ready",
            "bank_role_semantics_recovered",
            "event_binding_recovered",
        ):
            with self.subTest(key=key):
                self.assertFalse(report[key])
        self.assertIn("do not prove BNK field meanings", report["evidence_limit"])

    def test_rejects_non_text_and_malformed_arguments(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14AudioBankFormatTraceError,
            "expected source-qualified code in .text",
        ):
            audio_bank_format_trace_report(
                pe,
                windows=(("bad", 0x402010, 8),),
            )
        with self.assertRaisesRegex(
            Gate14AudioBankFormatTraceError,
            "with_disassembly must be boolean",
        ):
            audio_bank_format_trace_report(pe, windows=(), with_disassembly=1)

    def test_cli_keeps_private_output_and_format_state_unrecovered(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "bnk-format.json"
            argv = [
                "gate14_audio_bank_format_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--no-disassembly",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_audio_bank_format_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_audio_bank_format_source_trace.BANK_FORMAT_TRACE_WINDOWS",
                    (("synthetic loader", 0x401010, 8),),
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(emitted["sample_codec_recovered"])
            self.assertFalse(emitted["modern_sample_decode_ready"])
            self.assertFalse(emitted["event_binding_recovered"])


if __name__ == "__main__":
    unittest.main()
