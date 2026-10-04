"""Synthetic boundary tests for the private FastView draw-order tracer."""
from hashlib import sha256
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_draw_source_trace import (
    Gate14FastViewDrawTraceError,
    fastview_draw_trace_report,
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

    # Small valid x86 sequence in the source-qualified .text window.
    out[0x210:0x218] = b"\x55\x8b\xec\x68\x34\x20\x40\x00"
    target = 0x402034
    struct.pack_into("<I", out, 0x240, target)
    struct.pack_into("<I", out, 0x340, target)
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14FastViewDrawSourceTraceTests(unittest.TestCase):
    def test_collects_only_bounded_candidate_evidence_and_keeps_fidelity_false(self):
        report = fastview_draw_trace_report(
            parse_fixture(),
            with_disassembly=True,
            windows=(("synthetic draw", 0x401010, 0x10),),
            targets=(("synthetic target", 0x402034),),
        )

        self.assertEqual(len(report["windows"]), 1)
        window = report["windows"][0]
        self.assertEqual(window["label"], "synthetic draw")
        self.assertEqual(window["start_va"], 0x401010)
        self.assertEqual(window["section"], ".text")
        self.assertTrue(window["linear_disassembly_only"])

        candidates = report["target_candidates"][0][
            "raw_pointer_byte_candidates_not_proven_xrefs"
        ]
        self.assertEqual(
            [(item["candidate_va"], item["section"]) for item in candidates],
            [(0x401040, ".text"), (0x402040, ".rdata")],
        )
        self.assertFalse(report["child_list_direction_recovered"])
        self.assertFalse(report["cross_component_z_order_recovered"])
        self.assertFalse(report["picture_control_resize_semantics_recovered"])
        self.assertFalse(report["complete_fastview_frame_recovered"])
        self.assertIn("does not prove", report["evidence_limit"])

    def test_no_disassembly_mode_keeps_same_fail_closed_contract(self):
        report = fastview_draw_trace_report(
            parse_fixture(),
            with_disassembly=False,
            windows=(("synthetic draw", 0x401010, 0x08),),
            targets=(),
        )
        self.assertIsNone(report["windows"][0]["linear_disassembly_only"])
        self.assertEqual(report["target_candidates"], ())
        self.assertFalse(report["cross_component_z_order_recovered"])

    def test_rejects_non_text_window_and_invalid_inputs(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14FastViewDrawTraceError,
            "expected source-qualified code in .text",
        ):
            fastview_draw_trace_report(
                pe,
                windows=(("bad", 0x402010, 0x10),),
                targets=(),
            )
        with self.assertRaisesRegex(
            Gate14FastViewDrawTraceError,
            "with_disassembly must be boolean",
        ):
            fastview_draw_trace_report(
                pe,
                with_disassembly=1,
                windows=(),
                targets=(),
            )

    def test_cli_keeps_private_output_and_neutral_semantics(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "fastview-draw.json"
            argv = [
                "gate14_fastview_draw_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--no-disassembly",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_fastview_draw_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_fastview_draw_source_trace.FASTVIEW_DRAW_WINDOWS",
                    (("synthetic draw", 0x401010, 0x08),),
                ),
                patch(
                    "gate14_fastview_draw_source_trace.FASTVIEW_DRAW_TARGETS",
                    (),
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(emitted["cross_component_z_order_recovered"])
            self.assertFalse(emitted["picture_control_resize_semantics_recovered"])
            self.assertFalse(emitted["complete_fastview_frame_recovered"])


if __name__ == "__main__":
    unittest.main()
