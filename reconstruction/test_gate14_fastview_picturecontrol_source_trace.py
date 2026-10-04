"""Synthetic tests for the private Gate-14 PictureControl trace."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_picturecontrol_source_trace import (
    Gate14PictureControlTraceError,
    EMBEDDED_IMAGE_LAZY_ACQUIRE_VA,
    EMBEDDED_PICTURE_DRAW_LEAD_VA,
    EMBEDDED_PICTURE_SETUP_VA,
    LOW_LEVEL_PICTURE_BLIT_LEAD_VA,
    PICTURE_CONTROL_CHILD_RENDER_FORWARDER_VA,
    PictureControlVtableSlotCandidate,
    main as tracer_main,
    picturecontrol_trace_report,
    picturecontrol_vtable_slot_candidates,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x700)
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
    struct.pack_into("<IIII", out, second + 8, 0x100, 0x2000, 0x100, 0x500)

    # Three candidate methods.
    out[0x210:0x214] = b"\x55\x8b\xec\xc3"
    out[0x230:0x234] = b"\x55\x8b\xec\xc3"
    out[0x250:0x254] = b"\x55\x8b\xec\xc3"

    # A source-qualified trace window with a direct call-shaped byte sequence.
    out[0x280:0x286] = b"\xe8\x00\x00\x00\x00\xc3"

    vtable_va = 0x402020
    struct.pack_into("<III", out, 0x520, 0x401010, 0x401030, 0x401050)

    # Raw vtable pointer copy in .text. It remains only a byte candidate.
    struct.pack_into("<I", out, 0x2A0, vtable_va)
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14PictureControlSourceTraceTests(unittest.TestCase):
    def test_reads_bounded_candidate_slots_without_assigning_draw_semantics(self):
        slots = picturecontrol_vtable_slot_candidates(
            parse_fixture(),
            vtable_va=0x402020,
            max_slots=3,
            method_window_bytes=8,
            with_disassembly=True,
        )

        self.assertEqual(len(slots), 3)
        self.assertTrue(all(type(item) is PictureControlVtableSlotCandidate for item in slots))
        self.assertEqual(
            [item.target_va for item in slots],
            [0x401010, 0x401030, 0x401050],
        )
        self.assertEqual([item.slot_offset for item in slots], [0, 4, 8])
        self.assertTrue(all(item.target_section == ".text" for item in slots))
        self.assertTrue(all(item.candidate_method_window_bytes == 8 for item in slots))
        self.assertTrue(
            all(
                item.classification
                == "bounded_picturecontrol_vtable_slot_candidate_only"
                for item in slots
            )
        )
        self.assertTrue(all(item.linear_disassembly_only for item in slots))

    def test_report_retains_known_limits_and_raw_vtable_pointer_hits(self):
        pe = parse_fixture()
        report = picturecontrol_trace_report(
            pe,
            windows=(("synthetic renderer window", 0x401080, 6),),
            vtable_va=0x402020,
            max_slots=3,
            method_window_bytes=8,
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 1)
        self.assertEqual(report["windows"][0]["actual_window_bytes"], 6)
        self.assertEqual(
            report["windows"][0]["classification"],
            "bounded_source_window_not_function_boundary",
        )
        self.assertEqual(
            [
                (item["candidate_va"], item["section"])
                for item in report[
                    "raw_vtable_pointer_byte_occurrences_not_proven_xrefs"
                ]
            ],
            [(0x4010A0, ".text")],
        )
        self.assertFalse(report["cross_component_z_order_recovered"])
        self.assertFalse(report["picturecontrol_resize_pixels_recovered"])
        self.assertFalse(report["picturecontrol_crop_vs_stretch_recovered"])
        self.assertFalse(report["embedded_picture_source_rect_recovered"])
        self.assertFalse(report["child_registration_order_recovered"])
        self.assertEqual(
            tuple(item["va"] for item in report["renderer_chain_leads"]),
            (
                PICTURE_CONTROL_CHILD_RENDER_FORWARDER_VA,
                EMBEDDED_PICTURE_SETUP_VA,
                EMBEDDED_IMAGE_LAZY_ACQUIRE_VA,
                EMBEDDED_PICTURE_DRAW_LEAD_VA,
                LOW_LEVEL_PICTURE_BLIT_LEAD_VA,
            ),
        )
        self.assertIn("No virtual-slot role", report["evidence_limit"])

    def test_non_text_vtable_is_required_and_limits_fail_closed(self):
        pe = parse_fixture()

        with self.assertRaisesRegex(
            Gate14PictureControlTraceError,
            "must not reside in .text",
        ):
            picturecontrol_vtable_slot_candidates(
                pe,
                vtable_va=0x401010,
                max_slots=1,
            )
        with self.assertRaisesRegex(Gate14PictureControlTraceError, "max_slots"):
            picturecontrol_vtable_slot_candidates(
                pe,
                vtable_va=0x402020,
                max_slots=0,
            )
        with self.assertRaisesRegex(
            Gate14PictureControlTraceError,
            "method_window_bytes",
        ):
            picturecontrol_vtable_slot_candidates(
                pe,
                vtable_va=0x402020,
                method_window_bytes=0,
            )

    def test_cli_emits_private_neutral_candidate_report(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "picturecontrol.json"
            argv = [
                "gate14_fastview_picturecontrol_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--max-vtable-slots",
                "3",
                "--method-window-bytes",
                "8",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_fastview_picturecontrol_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate14_fastview_picturecontrol_source_trace.PICTURE_CONTROL_TRACE_WINDOWS",
                    (("synthetic renderer window", 0x401080, 6),),
                ),
                patch(
                    "gate14_fastview_picturecontrol_source_trace.PICTURE_CONTROL_VFTABLE_VA",
                    0x402020,
                ),
            ):
                # main passes its module constants through the report defaults;
                # patch the report to inject synthetic canonical addresses.
                with patch(
                    "gate14_fastview_picturecontrol_source_trace.picturecontrol_trace_report",
                    side_effect=lambda pe, **kwargs: picturecontrol_trace_report(
                        pe,
                        windows=(("synthetic renderer window", 0x401080, 6),),
                        vtable_va=0x402020,
                        max_slots=kwargs["max_slots"],
                        method_window_bytes=kwargs["method_window_bytes"],
                        with_disassembly=kwargs["with_disassembly"],
                    ),
                ):
                    self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(emitted["cross_component_z_order_recovered"])
            self.assertFalse(emitted["picturecontrol_resize_pixels_recovered"])
            self.assertFalse(emitted["picturecontrol_crop_vs_stretch_recovered"])
            self.assertFalse(emitted["embedded_picture_source_rect_recovered"])
            self.assertEqual(len(emitted["renderer_chain_leads"]), 5)
            self.assertNotIn("draw_order", emitted)
            self.assertNotIn("resize_rule", emitted)


if __name__ == "__main__":
    unittest.main()
