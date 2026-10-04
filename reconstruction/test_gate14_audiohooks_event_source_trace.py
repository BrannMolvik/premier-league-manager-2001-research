"""Synthetic boundary tests for the private Gate-14 AudioHooks caller tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_audiohooks_event_source_trace import (
    Gate14AudioHooksCallerTraceError,
    audiohooks_caller_trace_report,
    direct_audiohooks_call_candidates,
    main as tracer_main,
)
from gate14_audiohooks_menu_dispatch import AUDIO_HOOKS_DISPATCH_VA


def synthetic_pe() -> bytes:
    out = bytearray(0x1400)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x80)
    out[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", out, 0x84, 0x14C, 1)
    struct.pack_into("<H", out, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", out, option, 0x10B)
    struct.pack_into("<I", out, option + 28, 0x400000)
    sections = option + 0xE0

    out[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", out, sections + 8, 0x1100, 0x1DB000, 0x1100, 0x200)

    code_offset = 0x200 + 0x20
    call_va = 0x5DB024
    out[code_offset:code_offset + 2] = b"\x6A\x00"  # push 0
    out[code_offset + 2:code_offset + 4] = b"\x6A\x11"  # push 17
    out[code_offset + 4] = 0xE8
    displacement = AUDIO_HOOKS_DISPATCH_VA - (call_va + 5)
    struct.pack_into("<i", out, code_offset + 5, displacement)
    out[code_offset + 9] = 0xC3
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14AudioHooksCallerSourceTraceTests(unittest.TestCase):
    def test_finds_direct_call_candidate_and_nearby_push_values(self):
        rows = direct_audiohooks_call_candidates(parse_fixture())
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["callsite_va"], 0x5DB024)
        self.assertEqual(row["target_va"], AUDIO_HOOKS_DISPATCH_VA)
        self.assertEqual(
            row["classification"],
            "decoded_direct_audiohooks_call_candidate_not_cfg_or_semantic_proof",
        )
        pushes = row["nearby_push_operands_not_argument_proof"]
        self.assertEqual(
            [
                (
                    item["distance_from_call_instructions"],
                    item["operand_kind"],
                    item.get("immediate_value"),
                )
                for item in pushes[:2]
            ],
            [(1, "immediate", 17), (2, "immediate", 0)],
        )

    def test_report_keeps_all_semantic_and_calling_convention_flags_false(self):
        report = audiohooks_caller_trace_report(parse_fixture())
        self.assertEqual(report["candidate_count"], 1)
        self.assertFalse(report["direct_caller_cfg_recovered"])
        self.assertFalse(report["calling_convention_recovered"])
        self.assertFalse(report["event_argument_position_recovered"])
        self.assertFalse(report["state_argument_position_recovered"])
        self.assertFalse(report["semantic_event_binding_recovered"])
        self.assertFalse(report["sample_meaning_recovered"])
        self.assertIn("does not prove CFG reachability", report["evidence_limit"])

    def test_limits_and_target_validation_fail_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "context_instructions"
        ):
            direct_audiohooks_call_candidates(pe, context_instructions=0)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "max_candidates"
        ):
            direct_audiohooks_call_candidates(pe, max_candidates=0)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "target_va"
        ):
            direct_audiohooks_call_candidates(pe, target_va=-1)

    def test_nonmatching_direct_calls_are_not_promoted(self):
        pe = parse_fixture()
        rows = direct_audiohooks_call_candidates(pe, target_va=0x5DBF00)
        self.assertEqual(rows, ())

    def test_cli_writes_private_neutral_candidate_report(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "audiohooks-callers.json"
            argv = [
                "gate14_audiohooks_event_source_trace.py",
                str(source),
                "--output",
                str(output),
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_audiohooks_event_source_trace.require_private_output_path",
                    return_value=None,
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted["candidate_count"], 1)
            self.assertFalse(emitted["semantic_event_binding_recovered"])
            self.assertFalse(emitted["sample_meaning_recovered"])
            self.assertNotIn("event_names", emitted)
            self.assertNotIn("sample_names", emitted)


if __name__ == "__main__":
    unittest.main()
