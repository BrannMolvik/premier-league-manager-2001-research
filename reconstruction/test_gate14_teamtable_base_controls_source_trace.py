"""Synthetic tests for the private Gate-14 TeamTable base-control tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_teamtable_base_controls_source_trace import (
    Gate14TeamTableBaseTraceError,
    direct_known_control_calls,
    main as tracer_main,
    teamtable_base_trace_report,
)


def synthetic_pe() -> bytes:
    out = bytearray(0xA00)
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
    struct.pack_into("<IIII", out, sections + 8, 0x700, 0x1000, 0x700, 0x200)

    # owner at 0x401020:
    # push 6; call 0x401180; push 1; call 0x4011C0; ret
    out[0x220:0x222] = b"\x6a\x06"
    call_a = 0x401022
    out[0x222] = 0xE8
    struct.pack_into("<i", out, 0x223, 0x401180 - (call_a + 5))
    out[0x227:0x229] = b"\x6a\x01"
    call_b = 0x401029
    out[0x229] = 0xE8
    struct.pack_into("<i", out, 0x22A, 0x4011C0 - (call_b + 5))
    out[0x22E] = 0xC3

    out[0x380:0x384] = b"\x55\x8b\xec\xc3"
    out[0x3C0:0x3C4] = b"\x55\x8b\xec\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


WINDOWS = (("synthetic TeamTable owner", 0x401020, 0x60),)
TARGETS = (
    ("generic_picture_control", 0x401180),
    ("player_row", 0x4011C0),
)


class Gate14TeamTableBaseControlTraceTests(unittest.TestCase):
    def test_finds_known_constructor_calls_without_promoting_base_control_roles(self):
        calls = direct_known_control_calls(
            parse_fixture(),
            windows=WINDOWS,
            targets=TARGETS,
            context_instructions=4,
        )
        self.assertEqual(
            tuple((item.callsite_va, item.target_name) for item in calls),
            (
                (0x401022, "generic_picture_control"),
                (0x401029, "player_row"),
            ),
        )
        self.assertTrue(
            all(
                item.classification
                == "decoded_direct_teamtable_call_candidate_not_base_control_or_argument_proof"
                for item in calls
            )
        )
        self.assertNotIn(
            "base_control_index",
            calls[0].__dict__,
        )

    def test_report_preserves_known_count_and_every_missing_semantic(self):
        pe = parse_fixture()
        report = teamtable_base_trace_report(
            pe,
            windows=WINDOWS,
            targets=TARGETS,
            context_instructions=4,
            with_disassembly=True,
        )
        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(report["source_closed_team_table_base_control_count"], 6)
        self.assertTrue(report["team_table_base_control_count_recovered"])
        self.assertEqual(
            len(report["direct_known_control_calls_not_base_control_proof"]),
            2,
        )
        for key in (
            "team_table_base_control_identities_recovered",
            "team_table_base_control_constructor_calls_adjudicated",
            "team_table_base_control_registration_order_recovered",
            "team_table_base_control_geometry_recovered",
            "team_table_base_control_resources_recovered",
            "team_table_base_control_text_semantics_recovered",
            "team_table_base_control_pixels_rasterized",
            "complete_team_table",
            "complete_fastview_frame_recovered",
            "gate14_complete",
        ):
            self.assertFalse(report[key])
        self.assertIn("not proof", report["evidence_limit"])

    def test_bad_targets_windows_and_context_fail_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(Gate14TeamTableBaseTraceError, "targets"):
            direct_known_control_calls(
                pe,
                windows=WINDOWS,
                targets=(("bad",),),
            )
        with self.assertRaisesRegex(Gate14TeamTableBaseTraceError, "trace windows"):
            direct_known_control_calls(
                pe,
                windows=(("bad", 0x401020),),
                targets=TARGETS,
            )
        with self.assertRaisesRegex(
            Gate14TeamTableBaseTraceError,
            "context_instructions",
        ):
            direct_known_control_calls(
                pe,
                windows=WINDOWS,
                targets=TARGETS,
                context_instructions=0,
            )

    def test_cli_emits_private_neutral_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "teamtable-base.json"
            argv = [
                "gate14_teamtable_base_controls_source_trace.py",
                str(source),
                "--output",
                str(output),
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_teamtable_base_controls_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_teamtable_base_controls_source_trace.teamtable_base_trace_report",
                    side_effect=lambda pe, **kwargs: teamtable_base_trace_report(
                        pe,
                        windows=WINDOWS,
                        targets=TARGETS,
                        context_instructions=kwargs["context_instructions"],
                        with_disassembly=kwargs["with_disassembly"],
                    ),
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(emitted["team_table_base_control_count_recovered"])
            self.assertFalse(emitted["team_table_base_control_identities_recovered"])
            self.assertFalse(emitted["team_table_base_control_pixels_rasterized"])
            self.assertFalse(emitted["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
