"""Synthetic tests for the private Gate-14 score/table text source trace."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_static_text_source_trace import (
    Gate14FastViewStaticTextTraceError,
    direct_text_constructor_calls,
    main as tracer_main,
    static_text_trace_report,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x900)
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
    struct.pack_into("<IIII", out, sections + 8, 0x600, 0x1000, 0x600, 0x200)

    # owner window at VA 0x401020:
    # push 3; push 0x24; call 0x401180; ret
    off = 0x220
    out[off:off + 2] = b"\x6a\x03"
    out[off + 2:off + 4] = b"\x6a\x24"
    call_va = 0x401024
    target_va = 0x401180
    out[off + 4] = 0xE8
    struct.pack_into("<i", out, off + 5, target_va - (call_va + 5))
    out[off + 9] = 0xC3

    # generic target/window bytes.
    out[0x380:0x384] = b"\x55\x8b\xec\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


OWNER_WINDOWS = (("synthetic score row owner", 0x401020, 0x40),)
ALL_WINDOWS = (
    ("synthetic score row owner", 0x401020, 0x40),
    ("synthetic generic text", 0x401180, 0x20),
)


class Gate14FastViewStaticTextSourceTraceTests(unittest.TestCase):
    def test_finds_direct_text_constructor_call_without_assigning_arguments(self):
        rows = direct_text_constructor_calls(
            parse_fixture(),
            windows=OWNER_WINDOWS,
            target_va=0x401180,
            context_instructions=4,
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["owner_window"], "synthetic score row owner")
        self.assertEqual(row["callsite_va"], 0x401024)
        self.assertEqual(row["target_va"], 0x401180)
        self.assertEqual(
            row["classification"],
            "decoded_direct_textcontrol_call_candidate_not_argument_or_semantic_proof",
        )
        self.assertEqual(
            tuple(item["mnemonic"] for item in row["preceding_linear_context_not_argument_proof"]),
            ("push", "push"),
        )
        self.assertNotIn("arguments", row)
        self.assertNotIn("style_index", row)

    def test_report_keeps_every_new_text_fidelity_claim_fail_closed(self):
        pe = parse_fixture()
        report = static_text_trace_report(
            pe,
            windows=ALL_WINDOWS,
            text_owner_windows=OWNER_WINDOWS,
            target_va=0x401180,
            context_instructions=4,
            with_disassembly=True,
        )
        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 2)
        self.assertEqual(len(report["direct_textcontrol_calls_not_argument_proof"]), 1)
        self.assertTrue(report["static_text_control_geometry_recovered"])
        self.assertTrue(report["static_text_source_order_recovered"])
        self.assertTrue(report["argument_positions_recovered"])
        self.assertEqual(report["verified_constructor_this_register"], "ecx")
        self.assertEqual(report["verified_constructor_stack_cleanup_bytes"], 0x14)
        self.assertEqual(
            report["verified_constructor_five_argument_roles"],
            (
                "base_control_configuration",
                "rectangle_pointer",
                "native_control_flags",
                "source_string_object",
                "font_selector_index",
            ),
        )
        self.assertEqual(report["verified_league_table_row_heading_font_selector"], 0)
        self.assertFalse(report["user_facing_semantics_recovered"])
        self.assertFalse(report["final_text_values_recovered"])
        self.assertFalse(report["font_style_color_recovered"])
        self.assertFalse(report["pixels_rasterized"])
        self.assertFalse(report["score_subpanel_complete_pixels_recovered"])
        self.assertFalse(report["global_fastview_z_order_recovered"])
        self.assertFalse(report["complete_fastview_frame_recovered"])
        self.assertFalse(report["gate14_complete"])
        self.assertIn("not proof of argument positions", report["evidence_limit"])

    def test_bad_bounds_and_target_fail_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14FastViewStaticTextTraceError,
            "context_instructions",
        ):
            direct_text_constructor_calls(
                pe,
                windows=OWNER_WINDOWS,
                target_va=0x401180,
                context_instructions=0,
            )
        with self.assertRaisesRegex(
            Gate14FastViewStaticTextTraceError,
            "target_va",
        ):
            direct_text_constructor_calls(
                pe,
                windows=OWNER_WINDOWS,
                target_va=-1,
            )
        with self.assertRaisesRegex(
            Gate14FastViewStaticTextTraceError,
            "trace windows",
        ):
            direct_text_constructor_calls(
                pe,
                windows=(("bad", 0x401020),),
                target_va=0x401180,
            )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "static-text.json"
            argv = [
                "gate14_fastview_static_text_source_trace.py",
                str(source),
                "--output",
                str(output),
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_fastview_static_text_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_fastview_static_text_source_trace.static_text_trace_report",
                    side_effect=lambda pe, **kwargs: static_text_trace_report(
                        pe,
                        windows=ALL_WINDOWS,
                        text_owner_windows=OWNER_WINDOWS,
                        target_va=0x401180,
                        context_instructions=kwargs["context_instructions"],
                        with_disassembly=kwargs["with_disassembly"],
                    ),
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(emitted["argument_positions_recovered"])
            self.assertFalse(emitted["font_style_color_recovered"])
            self.assertFalse(emitted["pixels_rasterized"])
            self.assertNotIn("semantic_columns", emitted)
            self.assertNotIn("font_name", emitted)


if __name__ == "__main__":
    unittest.main()
