"""Synthetic tests for the private chant-enqueue caller tracer."""
from hashlib import sha256
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_chant_event_binding_source_trace import (
    ENQUEUE_VA,
    Gate14ChantEventBindingTraceError,
    chant_enqueue_call_candidates,
    chant_event_binding_trace_report,
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
    struct.pack_into("<IIII", out, sections + 8, 0x200, 0x1000, 0x200, 0x200)
    second = sections + 40
    out[second:second + 8] = b".rdata\x00\x00"
    struct.pack_into("<IIII", out, second + 8, 0x100, 0x2000, 0x100, 0x400)
    for index in range(0x200):
        out[0x200 + index] = (index * 7) & 0xFF
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


def fake_edges(*_args, **_kwargs):
    return (
        {
            "candidate_instruction_va": 0x401080,
            "candidate_target_va": ENQUEUE_VA,
            "candidate_target_labels": ("chant enqueue",),
            "candidate_mnemonic": "call",
            "candidate_bytes": "e800000000",
            "section": ".text",
            "classification": "linear_disassembly_only_unconfirmed_code_edge",
        },
        {
            "candidate_instruction_va": 0x401090,
            "candidate_target_va": ENQUEUE_VA,
            "candidate_target_labels": ("chant enqueue",),
            "candidate_mnemonic": "jmp",
            "candidate_bytes": "e900000000",
            "section": ".text",
            "classification": "linear_disassembly_only_unconfirmed_code_edge",
        },
    )


class Gate14ChantEventBindingTraceTests(unittest.TestCase):
    def test_retains_only_direct_calls_and_keeps_event_semantics_false(self):
        pe = parse_fixture()
        with patch(
            "gate14_chant_event_binding_source_trace.linear_direct_branch_candidates",
            side_effect=fake_edges,
        ):
            report = chant_event_binding_trace_report(pe)

        self.assertEqual(report["chant_enqueue_va"], 0x723360)
        self.assertEqual(report["direct_call_candidate_count"], 1)
        candidate = report["direct_call_candidates_not_cfg_proof"][0]
        self.assertEqual(candidate["candidate_instruction_va"], 0x401080)
        self.assertEqual(candidate["candidate_mnemonic"], "call")
        self.assertEqual(
            candidate["classification"],
            "linear_direct_call_candidate_to_chant_enqueue_not_cfg_or_event_proof",
        )
        self.assertIsNotNone(candidate["private_context_start_va"])
        self.assertTrue(candidate["private_context_raw_hex"])
        self.assertTrue(report["enqueue_runtime_recovered"])
        self.assertFalse(report["caller_cfg_recovered"])
        self.assertFalse(report["match_event_binding_recovered"])
        self.assertFalse(report["selector_event_meaning_recovered"])
        self.assertFalse(report["chant_meaning_recovered"])
        self.assertFalse(report["audio_ready"])

    def test_no_context_mode_does_not_emit_private_caller_bytes(self):
        pe = parse_fixture()
        with patch(
            "gate14_chant_event_binding_source_trace.linear_direct_branch_candidates",
            side_effect=fake_edges,
        ):
            candidates = chant_enqueue_call_candidates(
                pe,
                include_private_windows=False,
            )
        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0]["private_context_start_va"])
        self.assertIsNone(candidates[0]["private_context_raw_hex"])

    def test_invalid_context_flag_fails_closed(self):
        with self.assertRaisesRegex(
            Gate14ChantEventBindingTraceError,
            "include_private_windows must be boolean",
        ):
            chant_enqueue_call_candidates(
                parse_fixture(),
                include_private_windows=1,
            )

    def test_cli_writes_private_candidate_report_without_event_promotion(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "chant-callers.json"
            argv = [
                "gate14_chant_event_binding_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--no-context-windows",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_chant_event_binding_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_chant_event_binding_source_trace.linear_direct_branch_candidates",
                    side_effect=fake_edges,
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted["direct_call_candidate_count"], 1)
            self.assertFalse(emitted["match_event_binding_recovered"])
            self.assertFalse(emitted["selector_event_meaning_recovered"])
            self.assertFalse(emitted["audio_ready"])


if __name__ == "__main__":
    unittest.main()
