"""Synthetic boundary tests for the private Gate-14 .bnk source tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_audio_bank_source_trace import (
    Gate14AudioBankTraceError,
    audio_bank_trace_report,
    embedded_bnk_string_candidates,
    main as tracer_main,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x500)
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
    struct.pack_into("<IIII", out, sections + 8, 0x100, 0x1000, 0x100, 0x200)
    second = sections + 40
    out[second:second + 8] = b".rdata\x00\x00"
    struct.pack_into("<IIII", out, second + 8, 0x100, 0x2000, 0x100, 0x300)

    first = b"Audio/MenuMusic.BNK\x00"
    second_name = b"Sound\\Match\\crowd.bnk\x00"
    out[0x310:0x310 + len(first)] = first
    out[0x340:0x340 + len(second_name)] = second_name
    out[0x370:0x37C] = b"notbank.txt\x00"

    first_va = 0x402010
    second_va = 0x402040
    struct.pack_into("<I", out, 0x220, first_va)
    struct.pack_into("<I", out, 0x224, second_va)
    struct.pack_into("<I", out, 0x380, first_va)
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14AudioBankSourceTraceTests(unittest.TestCase):
    def test_finds_case_insensitive_null_terminated_bnk_strings_and_exact_vas(self):
        candidates = embedded_bnk_string_candidates(parse_fixture())
        self.assertEqual(
            [(item["string_va"], item["section"], item["embedded_text"])
             for item in candidates],
            [
                (0x402010, ".rdata", "Audio/MenuMusic.BNK"),
                (0x402040, ".rdata", "Sound\\Match\\crowd.bnk"),
            ],
        )
        self.assertTrue(all("candidate_only" in item["classification"]
                            for item in candidates))

    def test_reports_raw_pointer_candidates_without_promoting_xrefs(self):
        report = audio_bank_trace_report(parse_fixture())
        first, second = report["embedded_bnk_candidates"]
        self.assertEqual(report["candidate_count"], 2)
        self.assertFalse(report["bank_semantics_recovered"])
        self.assertFalse(report["bank_event_bindings_recovered"])
        self.assertIn("not proven x86 xrefs", report["evidence_limit"])
        self.assertEqual(
            [(item["candidate_va"], item["section"])
             for item in first["raw_pointer_byte_candidates_not_proven_xrefs"]],
            [(0x401020, ".text"), (0x402080, ".rdata")],
        )
        self.assertEqual(
            [(item["candidate_va"], item["section"])
             for item in second["raw_pointer_byte_candidates_not_proven_xrefs"]],
            [(0x401024, ".text")],
        )

    def test_limits_fail_closed_or_truncate_without_semantic_promotion(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(Gate14AudioBankTraceError, "max_strings"):
            embedded_bnk_string_candidates(pe, max_strings=0)
        with self.assertRaisesRegex(
            Gate14AudioBankTraceError, "max_pointer_candidates"
        ):
            embedded_bnk_string_candidates(pe, max_pointer_candidates=0)
        candidates = embedded_bnk_string_candidates(pe, max_strings=1)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["embedded_text"], "Audio/MenuMusic.BNK")

    def test_cli_writes_only_neutral_private_candidate_report(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "audio-bank-candidates.json"
            argv = [
                "gate14_audio_bank_source_trace.py",
                str(source),
                "--output",
                str(output),
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_audio_bank_source_trace.require_private_output_path",
                    return_value=None,
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted["candidate_count"], 2)
            self.assertFalse(emitted["bank_semantics_recovered"])
            self.assertFalse(emitted["bank_event_bindings_recovered"])
            self.assertNotIn("menu_music_bank", emitted)
            self.assertNotIn("match_sound_bank", emitted)


if __name__ == "__main__":
    unittest.main()
