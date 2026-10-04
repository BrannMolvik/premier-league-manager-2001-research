"""Synthetic tests for the bounded FastView owner-order source tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_owner_order_source_trace import (
    FASTVIEW_OWNER_NEIGHBORHOOD_END_VA,
    FASTVIEW_OWNER_NEIGHBORHOOD_START_VA,
    POSSESSION_DIAGRAM_CONSTRUCTOR_VA,
    Gate14FastViewOwnerOrderTraceError,
    fastview_owner_call_candidates,
    fastview_owner_order_trace_report,
    main as tracer_main,
)
from gate14_fastview_team import FASTVIEW_TEAM_CONSTRUCTOR_VA


def _emit_call(out: bytearray, raw_offset: int, call_va: int, target_va: int) -> None:
    out[raw_offset] = 0xE8
    struct.pack_into("<i", out, raw_offset + 1, target_va - (call_va + 5))


def synthetic_pe() -> bytes:
    out = bytearray(0x2600)
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
    # VA 0x51F000..0x5213FF, file-backed from 0x200.
    struct.pack_into("<IIII", out, sections + 8, 0x2400, 0x11F000, 0x2400, 0x200)
    out[0x200:0x2600] = b"\x90" * 0x2400

    first_va = 0x51F4A0
    first_raw = 0x200 + (first_va - 0x51F000)
    _emit_call(out, first_raw, first_va, FASTVIEW_TEAM_CONSTRUCTOR_VA)

    second_va = 0x5206CD
    second_raw = 0x200 + (second_va - 0x51F000)
    _emit_call(out, second_raw, second_va, POSSESSION_DIAGRAM_CONSTRUCTOR_VA)

    unrelated_va = 0x520700
    unrelated_raw = 0x200 + (unrelated_va - 0x51F000)
    _emit_call(out, unrelated_raw, unrelated_va, 0x500000)

    out[0x200 + (0x5208F0 - 0x51F000)] = 0xC3
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14FastViewOwnerOrderSourceTraceTests(unittest.TestCase):
    def test_finds_only_known_constructor_targets_inside_bounded_owner_region(self):
        rows = fastview_owner_call_candidates(parse_fixture())
        self.assertEqual(
            [(row.callsite_va, row.target_name, row.target_va) for row in rows],
            [
                (0x51F4A0, "fastview_team", FASTVIEW_TEAM_CONSTRUCTOR_VA),
                (0x5206CD, "possession_diagram", POSSESSION_DIAGRAM_CONSTRUCTOR_VA),
            ],
        )
        for row in rows:
            self.assertEqual(row.section, ".text")
            self.assertIn("not_cfg_parent_or_draw_order_proof", row.classification)
            self.assertTrue(row.bounded_linear_context)

    def test_report_keeps_every_new_order_claim_false(self):
        report = fastview_owner_order_trace_report(parse_fixture())
        self.assertEqual(report["candidate_count"], 2)
        self.assertFalse(report["fastview_team_owner_callsite_recovered"])
        self.assertFalse(report["same_parent_registration_recovered_for_new_pairs"])
        self.assertFalse(report["additional_pairwise_draw_order_recovered"])
        self.assertFalse(report["global_fastview_z_order_recovered"])
        self.assertFalse(report["cross_component_blend_rule_recovered"])
        self.assertFalse(report["complete_fastview_frame_recovered"])
        self.assertIn("does not prove", report["evidence_limit"])
        self.assertEqual(
            report["bounded_owner_neighborhood"]["start_va"],
            FASTVIEW_OWNER_NEIGHBORHOOD_START_VA,
        )
        self.assertEqual(
            report["bounded_owner_neighborhood"]["end_va_exclusive"],
            FASTVIEW_OWNER_NEIGHBORHOOD_END_VA,
        )

    def test_reference_rows_are_calibration_only(self):
        report = fastview_owner_order_trace_report(parse_fixture())
        refs = {row["name"]: row for row in report["known_reference_callsites"]}
        self.assertTrue(refs["possession_diagram"]["decoded_in_this_report"])
        self.assertFalse(refs["top_bar_picture_control"]["decoded_in_this_report"])
        self.assertEqual(
            refs["possession_diagram"]["status"],
            "persisted_source_reference_only",
        )

    def test_invalid_bounds_context_and_duplicate_targets_fail_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14FastViewOwnerOrderTraceError,
            "increasing uint32 range",
        ):
            fastview_owner_call_candidates(pe, start_va=10, end_va=10)
        with self.assertRaisesRegex(
            Gate14FastViewOwnerOrderTraceError,
            "context_instructions",
        ):
            fastview_owner_call_candidates(pe, context_instructions=0)
        with self.assertRaisesRegex(
            Gate14FastViewOwnerOrderTraceError,
            "target VAs must be unique",
        ):
            fastview_owner_call_candidates(
                pe,
                targets=(("a", 0x500000), ("b", 0x500000)),
            )

    def test_cli_writes_private_fail_closed_report(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "fastview-owner-order.json"
            argv = [
                "gate14_fastview_owner_order_source_trace.py",
                str(source),
                "--output",
                str(output),
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_fastview_owner_order_source_trace.require_private_output_path",
                    return_value=None,
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted["candidate_count"], 2)
            self.assertFalse(emitted["additional_pairwise_draw_order_recovered"])
            self.assertFalse(emitted["global_fastview_z_order_recovered"])


if __name__ == "__main__":
    unittest.main()
