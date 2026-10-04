"""Synthetic boundary tests for the private Gate-14 AudioHooks sender tracer."""
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
from gate14_audiohooks_event_source_trace import (
    AUDIO_HOOKS_ARGUMENT_BYTES,
    AUDIO_HOOKS_DISPATCH_VA,
    AUDIO_HOOKS_EVENT_STACK_OFFSET,
    AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA,
    AUDIO_HOOKS_INSTALL_GLOBAL_PTR_VA,
    AUDIO_HOOKS_INSTALL_VTABLE_VA,
    AUDIO_HOOKS_STATE_STACK_OFFSET,
    AUDIO_HOOKS_THIRD_STACK_OFFSET,
    AUDIO_HOOKS_VTABLE_SLOT0_TARGET_VA,
    AUDIO_HOOKS_VTABLE_VA,
    BUTTON_EASE_DECORATED_RTTI,
    BUTTON_EASE_EVENT_IDS,
    BUTTON_EASE_EVENT_SELECTOR_OBJECT_FIELD,
    BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_OFFSET,
    BUTTON_EASE_EVENT_SELECTOR_VA,
    BUTTON_EASE_EVENT_SELECTOR_WORD_FIELD,
    BUTTON_EASE_INPUT_VA,
    BUTTON_EASE_TYPE_DESCRIPTOR_VA,
    BUTTON_EASE_VTABLE_VA,
    SOURCE_CALLING_CONVENTION,
    SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS,
    SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS,
    SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS,
    Gate14AudioHooksCallerTraceError,
    audiohooks_caller_trace_report,
    direct_audiohooks_call_candidates,
    main as tracer_main,
    virtual_audiohooks_call_candidates,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x1800)
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
    struct.pack_into("<IIII", out, sections + 8, 0x1500, 0x1DB000, 0x1500, 0x200)
    out[0x200:0x1700] = b"\x90" * 0x1500

    # Direct CALL calibration candidate.
    direct_off = 0x220
    direct_call_va = 0x5DB024
    out[direct_off:direct_off + 2] = b"\x6A\x00"  # push arg3
    out[direct_off + 2:direct_off + 4] = b"\x6A\x11"  # push state
    out[direct_off + 4] = 0xE8
    displacement = AUDIO_HOOKS_DISPATCH_VA - (direct_call_va + 5)
    struct.pack_into("<i", out, direct_off + 5, displacement)
    out[direct_off + 9] = 0xC3

    # Canonical virtual shape:
    # mov ecx,[0x984810]; mov edx,[ecx]; push 0; push 1; push 1; call [edx]
    virtual_off = 0x300
    out[virtual_off:virtual_off + 6] = b"\x8B\x0D" + struct.pack(
        "<I", AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA
    )
    out[virtual_off + 6:virtual_off + 8] = b"\x8B\x11"
    out[virtual_off + 8:virtual_off + 10] = b"\x6A\x00"
    out[virtual_off + 10:virtual_off + 12] = b"\x6A\x01"
    out[virtual_off + 12:virtual_off + 14] = b"\x6A\x01"
    out[virtual_off + 14:virtual_off + 16] = b"\xFF\x12"
    out[virtual_off + 16] = 0xC3
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate14AudioHooksCallerSourceTraceTests(unittest.TestCase):
    def test_source_anchor_and_calling_convention_contract(self):
        self.assertEqual(AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA, 0x984810)
        self.assertEqual(AUDIO_HOOKS_VTABLE_VA, 0x7D73EC)
        self.assertEqual(AUDIO_HOOKS_VTABLE_SLOT0_TARGET_VA, 0x5DBFC0)
        self.assertEqual(AUDIO_HOOKS_INSTALL_VTABLE_VA, 0x5DC2B6)
        self.assertEqual(AUDIO_HOOKS_INSTALL_GLOBAL_PTR_VA, 0x5DC2BC)
        self.assertEqual(AUDIO_HOOKS_EVENT_STACK_OFFSET, 4)
        self.assertEqual(AUDIO_HOOKS_STATE_STACK_OFFSET, 8)
        self.assertEqual(AUDIO_HOOKS_THIRD_STACK_OFFSET, 12)
        self.assertEqual(AUDIO_HOOKS_ARGUMENT_BYTES, 12)

        self.assertFalse(SOURCE_CALLING_CONVENTION.third_argument_read_by_dispatcher)
        self.assertFalse(SOURCE_CALLING_CONVENTION.semantic_event_binding_recovered)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError,
            "does not read",
        ):
            replace(SOURCE_CALLING_CONVENTION, third_argument_read_by_dispatcher=True)

    def test_finds_direct_call_candidate_and_nearby_push_values(self):
        rows = direct_audiohooks_call_candidates(parse_fixture())
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["callsite_va"], 0x5DB024)
        self.assertEqual(row["target_va"], AUDIO_HOOKS_DISPATCH_VA)
        self.assertIn("not_cfg_or_semantic_proof", row["classification"])

    def test_finds_global_object_vtable_slot0_call_candidate(self):
        rows = virtual_audiohooks_call_candidates(parse_fixture())
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["global_load_va"], 0x5DB100)
        self.assertEqual(row["callsite_va"], 0x5DB10E)
        self.assertEqual(row["global_va"], AUDIO_HOOKS_GLOBAL_OBJECT_PTR_VA)
        self.assertEqual(row["vtable_slot_byte_offset"], 0)
        self.assertIn("global_audiohooks_slot0", row["classification"])
        pushes = row["nearby_push_operands_not_argument_proof"]
        self.assertEqual(
            [item.get("immediate_value") for item in pushes[:3]],
            [1, 1, 0],
        )

    def test_button_ease_dynamic_event_selector_is_source_closed_to_two_numeric_ids(self):
        self.assertEqual(BUTTON_EASE_DECORATED_RTTI, ".?AVButton@ease_2001@@")
        self.assertEqual(BUTTON_EASE_TYPE_DESCRIPTOR_VA, 0x81AD90)
        self.assertEqual(BUTTON_EASE_VTABLE_VA, 0x7BF4CC)
        self.assertEqual(BUTTON_EASE_EVENT_SELECTOR_VA, 0x6528A0)
        self.assertEqual(BUTTON_EASE_INPUT_VA, 0x64F7A0)
        self.assertEqual(BUTTON_EASE_EVENT_IDS, (2, 10))
        self.assertEqual(BUTTON_EASE_EVENT_SELECTOR_OBJECT_FIELD, 0x34)
        self.assertEqual(BUTTON_EASE_EVENT_SELECTOR_WORD_FIELD, 0x4A)
        self.assertEqual(BUTTON_EASE_EVENT_SELECTOR_VIRTUAL_OFFSET, 0xA8)

        report = audiohooks_caller_trace_report(parse_fixture())
        contract = report["button_ease_source_contract"]
        self.assertEqual(tuple(contract["event_ids"]), (2, 10))
        self.assertFalse(contract["event_semantics_recovered"])
        self.assertEqual(
            tuple(report["source_closed_dynamic_control_event_ids"]),
            (2, 10),
        )

    def test_source_closed_literal_and_dynamic_sender_families_are_numeric_only(self):
        self.assertEqual(len(SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS), 10)
        self.assertIn((0x47AD13, 13, 0, 0), SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS)
        self.assertIn((0x4D707F, 19, 0, 0), SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS)
        self.assertIn((0x5EC1BC, 11, 0, 0), SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS)

        self.assertEqual(len(SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS), 10)
        self.assertEqual(SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS[0], (0x64F7FE, 0, 0x40))
        self.assertEqual(SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS[-1], (0x64FD8B, 8, 0x40))

        self.assertEqual(len(SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS), 7)
        self.assertIn(
            (0x5EB69B, (23, 25), 0, 0, "event_two_value_branch"),
            SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS,
        )
        self.assertIn(
            (0x5EBA8A, (24, 26), 0, 0, "event_two_value_branch"),
            SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS,
        )
        self.assertIn(
            (0x5ED5E5, (17, 18), 0, 0, "event_two_value_branch"),
            SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS,
        )
        self.assertNotIn("menu", repr(SOURCE_CLOSED_LITERAL_VIRTUAL_SENDERS).lower())
        self.assertNotIn("click", repr(SOURCE_CLOSED_DYNAMIC_CONTROL_SENDERS).lower())
        self.assertNotIn("sample", repr(SOURCE_CLOSED_DERIVED_VIRTUAL_SENDERS).lower())

    def test_report_promotes_structure_but_not_event_or_sample_meaning(self):
        report = audiohooks_caller_trace_report(parse_fixture())
        self.assertTrue(report["rtti_vtable_global_path_recovered"])
        self.assertTrue(report["calling_convention_recovered"])
        self.assertTrue(report["event_argument_position_recovered"])
        self.assertTrue(report["state_argument_position_recovered"])
        self.assertTrue(report["third_argument_position_recovered"])
        self.assertTrue(report["third_argument_unused_by_dispatcher_recovered"])
        self.assertFalse(report["semantic_event_binding_recovered"])
        self.assertFalse(report["sample_meaning_recovered"])
        self.assertIn("not human-readable", report["evidence_limit"])

    def test_limits_and_global_validation_fail_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "context_instructions"
        ):
            direct_audiohooks_call_candidates(pe, context_instructions=0)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "at least three"
        ):
            virtual_audiohooks_call_candidates(pe, context_instructions=2)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "global_va"
        ):
            virtual_audiohooks_call_candidates(pe, global_va=-1)
        with self.assertRaisesRegex(
            Gate14AudioHooksCallerTraceError, "max_candidates"
        ):
            virtual_audiohooks_call_candidates(pe, max_candidates=0)

    def test_cli_writes_private_numeric_sender_report(self):
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
            self.assertEqual(emitted["virtual_candidate_count"], 1)
            self.assertFalse(emitted["semantic_event_binding_recovered"])
            self.assertFalse(emitted["sample_meaning_recovered"])
            self.assertNotIn("event_names", emitted)
            self.assertNotIn("sample_names", emitted)


if __name__ == "__main__":
    unittest.main()
