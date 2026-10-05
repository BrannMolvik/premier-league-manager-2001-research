"""Synthetic tests for the private Gate-15 support-staff cost tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate15_support_staff_cost_source_trace import (
    CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET,
    Gate15SupportStaffCostTraceError,
    main as tracer_main,
    resolve_vtable_slot_target,
    support_staff_cost_trace_report,
)


IMAGE_BASE = 0x400000
TEXT_VA = 0x401000
RDATA_VA = 0x402000
SYNTH_VTABLE_VA = 0x402100


def synthetic_pe() -> bytes:
    out = bytearray(0xE00)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x80)
    out[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", out, 0x84, 0x14C, 2)
    struct.pack_into("<H", out, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", out, option, 0x10B)
    struct.pack_into("<I", out, option + 28, IMAGE_BASE)
    sections = option + 0xE0

    out[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", out, sections + 8, 0x600, 0x1000, 0x600, 0x200)

    second = sections + 40
    out[second:second + 8] = b".rdata\x00\x00"
    struct.pack_into("<IIII", out, second + 8, 0x400, 0x2000, 0x400, 0x800)

    # Three tiny virtual targets in .text.
    for target_va, raw in (
        (0x401100, b"\xb8\x03\x00\x00\x00\xc3"),
        (0x401180, b"\x8b\x41\x10\xc3"),
        (0x4011C0, b"\x8b\x41\x10\xc3"),
    ):
        off = 0x200 + (target_va - TEXT_VA)
        out[off:off + len(raw)] = raw

    # Synthetic CSupportStaff vtable entries corresponding to +0x14/+0x24/+0x40.
    vtable_raw = 0x800 + (SYNTH_VTABLE_VA - RDATA_VA)
    struct.pack_into("<I", out, vtable_raw + 0x14, 0x401100)
    struct.pack_into("<I", out, vtable_raw + 0x24, 0x401180)
    struct.pack_into("<I", out, vtable_raw + 0x40, 0x4011C0)
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


SYNTH_WINDOWS = (
    ("synthetic monthly caller", 0x401020, 0x20),
    ("synthetic constructor", 0x401060, 0x20),
)
SYNTH_SLOTS = (
    ("staff_type", 0x14, True),
    ("monthly_cost_value", 0x24, False),
    ("effective_training_rating", 0x40, True),
)


class Gate15SupportStaffCostSourceTraceTests(unittest.TestCase):
    def test_resolves_exact_vtable_slot_pointer_without_promoting_semantics(self):
        pe = parse_fixture()
        row = resolve_vtable_slot_target(
            pe,
            SYNTH_VTABLE_VA,
            CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET,
        )
        self.assertEqual(row["entry_va"], SYNTH_VTABLE_VA + 0x24)
        self.assertEqual(row["target_va"], 0x401180)
        self.assertEqual(row["target_section"], ".text")
        self.assertEqual(
            row["classification"],
            "resolved_vtable_pointer_not_new_semantic_proof",
        )

    def test_report_keeps_amount_materialization_fail_closed(self):
        pe = parse_fixture()
        with patch(
            "gate15_support_staff_cost_source_trace.CSUPPORTSTAFF_VTABLE_VA",
            SYNTH_VTABLE_VA,
        ):
            report = support_staff_cost_trace_report(
                pe,
                windows=SYNTH_WINDOWS,
                slot_roles=SYNTH_SLOTS,
                with_disassembly=True,
                target_window_size=0x20,
            )

        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(report["cost_virtual_target_va"], 0x401180)
        self.assertTrue(report["cost_virtual_target_pointer_resolved"])
        self.assertFalse(report["cost_virtual_value_semantics_recovered"])
        self.assertFalse(report["cost_virtual_backing_field_recovered"])
        self.assertFalse(report["cost_virtual_constructor_initialization_recovered"])
        self.assertFalse(report["cost_virtual_save_load_roundtrip_recovered"])
        self.assertFalse(report["monthly_support_staff_amount_materialized"])
        self.assertFalse(report["gate15_support_staff_cost_gap_closed"])
        self.assertFalse(report["gate15_complete"])
        self.assertEqual(
            report["monthly_cost_contract_already_recovered"]["balance_category"],
            102,
        )
        self.assertIn("does not prove", report["evidence_limit"])

    def test_bad_slot_offsets_and_non_text_targets_fail_closed(self):
        pe = parse_fixture()
        for offset in (-4, 2, 0x404, True):
            with self.subTest(offset=offset):
                with self.assertRaises(Gate15SupportStaffCostTraceError):
                    resolve_vtable_slot_target(pe, SYNTH_VTABLE_VA, offset)

        raw = bytearray(synthetic_pe())
        vtable_raw = 0x800 + (SYNTH_VTABLE_VA - RDATA_VA)
        struct.pack_into("<I", raw, vtable_raw + 0x24, SYNTH_VTABLE_VA)
        malformed = OriginalPE32.parse(
            bytes(raw),
            expected_sha256=sha256(bytes(raw)).hexdigest(),
        )
        with self.assertRaisesRegex(
            Gate15SupportStaffCostTraceError,
            "does not resolve into .text",
        ):
            resolve_vtable_slot_target(
                malformed,
                SYNTH_VTABLE_VA,
                CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET,
            )

    def test_bad_report_inputs_fail_closed(self):
        pe = parse_fixture()
        with patch(
            "gate15_support_staff_cost_source_trace.CSUPPORTSTAFF_VTABLE_VA",
            SYNTH_VTABLE_VA,
        ):
            with self.assertRaises(Gate15SupportStaffCostTraceError):
                support_staff_cost_trace_report(
                    pe,
                    windows=(("bad", 0x401020),),
                    slot_roles=SYNTH_SLOTS,
                )
            for size in (0x0F, 0x1001, True):
                with self.subTest(size=size):
                    with self.assertRaises(Gate15SupportStaffCostTraceError):
                        support_staff_cost_trace_report(
                            pe,
                            windows=SYNTH_WINDOWS,
                            slot_roles=SYNTH_SLOTS,
                            target_window_size=size,
                        )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "staff-cost.json"
            argv = [
                "gate15_support_staff_cost_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--target-window-size",
                "0x20",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate15_support_staff_cost_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate15_support_staff_cost_source_trace.CSUPPORTSTAFF_VTABLE_VA",
                    SYNTH_VTABLE_VA,
                ),
                patch(
                    "gate15_support_staff_cost_source_trace.STATIC_TRACE_WINDOWS",
                    SYNTH_WINDOWS,
                ),
                patch(
                    "gate15_support_staff_cost_source_trace.KNOWN_SLOT_ROLES",
                    SYNTH_SLOTS,
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted["cost_virtual_target_va"], 0x401180)
            self.assertFalse(emitted["monthly_support_staff_amount_materialized"])
            self.assertFalse(emitted["gate15_support_staff_cost_gap_closed"])
            self.assertFalse(emitted["gate15_complete"])


if __name__ == "__main__":
    unittest.main()
