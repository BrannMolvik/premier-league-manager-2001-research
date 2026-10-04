"""Synthetic tests for the private Gate-14 font-blend tracer."""
from hashlib import sha256
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_font_blend_source_trace import (
    FONT_DRAW_VA,
    FONT_LOADER_VA,
    GENERIC_TEXT_DRAW_VA,
    NATIVE_COLOR_SETTER_VA,
    POSSESSION_TEXT_FONT_OBJECT_VA,
    POSSESSION_TEXT_FONT_WRAPPER_VA,
    POSSESSION_TEXT_STYLE_SELECTOR_VA,
    Gate14FontBlendTraceError,
    classify_font_blend_dataflow_candidates,
    font_blend_trace_report,
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
    out[0x210:0x220] = (
        b"\x55\x8b\xec"
        b"\x8b\x41\x10"          # mov eax,[ecx+0x10] read
        b"\x89\x47\x04"          # mov [edi+4],eax write
        b"\x6a\x7f"               # push 0x7f
        b"\x5d\xc3\x90\x90\x90"
    )
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14FontBlendSourceTraceTests(unittest.TestCase):
    def test_collects_bounded_font_windows_without_blend_promotion(self):
        pe = parse_fixture()
        report = font_blend_trace_report(
            pe,
            windows=(("synthetic font draw", 0x401010, 8),),
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 1)
        self.assertEqual(report["windows"][0]["section"], ".text")
        self.assertEqual(report["windows"][0]["actual_window_bytes"], 8)
        self.assertTrue(report["windows"][0]["linear_disassembly_only"])
        self.assertTrue(report["glyph_alpha_source_recovered"])
        self.assertTrue(report["possession_pairwise_draw_order_recovered"])
        self.assertFalse(report["glyph_destination_read_recovered"])
        self.assertFalse(report["glyph_alpha_blend_rule_recovered"])
        self.assertFalse(report["native_color_channel_layout_recovered"])
        self.assertFalse(report["cross_component_pixels_resolvable"])
        self.assertFalse(report["complete_fastview_frame_recovered"])
        self.assertIn("do not yet prove", report["evidence_limit"])

    def test_classifies_memory_access_direction_without_blend_promotion(self):
        pe = parse_fixture()
        candidates = classify_font_blend_dataflow_candidates(
            pe,
            windows=(("synthetic font draw", 0x401010, 0x10),),
        )
        by_va = {item["instruction_va"]: item for item in candidates}

        self.assertEqual(
            by_va[0x401013]["memory_operand_candidates"],
            (
                {
                    "operand_index": 1,
                    "base": "ecx",
                    "index": None,
                    "scale": 1,
                    "displacement": 0x10,
                    "operand_size": 4,
                    "access": "read",
                },
            ),
        )
        self.assertEqual(
            by_va[0x401016]["memory_operand_candidates"],
            (
                {
                    "operand_index": 0,
                    "base": "edi",
                    "index": None,
                    "scale": 1,
                    "displacement": 4,
                    "operand_size": 4,
                    "access": "write",
                },
            ),
        )
        self.assertIn(0x7F, by_va[0x401019]["immediate_candidates"])
        self.assertEqual(
            by_va[0x401013]["classification"],
            "bounded_linear_font_dataflow_candidate_not_framebuffer_or_blend_proof",
        )

        report = font_blend_trace_report(
            pe,
            windows=(("synthetic font draw", 0x401010, 0x10),),
            classify_dataflow_candidates=True,
        )
        self.assertTrue(report["font_dataflow_candidates_classified"])
        self.assertTrue(report["bounded_font_dataflow_candidates_not_blend_proof"])
        self.assertFalse(report["glyph_destination_read_recovered"])
        self.assertFalse(report["glyph_alpha_blend_rule_recovered"])
        self.assertFalse(report["native_color_channel_layout_recovered"])

    def test_source_anchor_constants_remain_exact(self):
        self.assertEqual(GENERIC_TEXT_DRAW_VA, 0x64F090)
        self.assertEqual(NATIVE_COLOR_SETTER_VA, 0x650480)
        self.assertEqual(FONT_DRAW_VA, 0x657280)
        self.assertEqual(FONT_LOADER_VA, 0x657650)
        self.assertEqual(POSSESSION_TEXT_STYLE_SELECTOR_VA, 0x527BA0)
        self.assertEqual(POSSESSION_TEXT_FONT_OBJECT_VA, 0x9197E0)
        self.assertEqual(POSSESSION_TEXT_FONT_WRAPPER_VA, 0x87BE90)

    def test_rejects_non_text_or_malformed_windows(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14FontBlendTraceError,
            "expected source-qualified code in .text",
        ):
            font_blend_trace_report(
                pe,
                windows=(("bad", 0x402010, 8),),
            )
        with self.assertRaisesRegex(
            Gate14FontBlendTraceError,
            "with_disassembly must be boolean",
        ):
            font_blend_trace_report(pe, windows=(), with_disassembly=1)

    def test_cli_keeps_private_output_and_neutral_blend_state(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "font-blend.json"
            argv = [
                "gate14_font_blend_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--no-disassembly",
                "--classify-dataflow-candidates",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_font_blend_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_font_blend_source_trace.FONT_BLEND_TRACE_WINDOWS",
                    (("synthetic font draw", 0x401010, 8),),
                ),
            ):
                self.assertEqual(tracer_main(), 0)
            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(emitted["font_dataflow_candidates_classified"])
            self.assertTrue(emitted["bounded_font_dataflow_candidates_not_blend_proof"])
            self.assertFalse(emitted["glyph_alpha_blend_rule_recovered"])
            self.assertFalse(emitted["cross_component_pixels_resolvable"])
            self.assertFalse(emitted["complete_fastview_frame_recovered"])


if __name__ == "__main__":
    unittest.main()
