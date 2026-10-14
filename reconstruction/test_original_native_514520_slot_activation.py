"""Original native 514520 reached node+8/embedded SideRef source decisions."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into
import unittest

from original_native_514520_slot_activation import (
    OriginalNative514520SourceError,
    source_original_514520_reached_slot_activation,
)


def node(*,state=0,vt=0x7C4D70):
    raw=bytearray(0x0C)
    pack_into("<I",raw,0,vt)
    pack_into("<I",raw,0x08,state)
    return bytes(raw)


def event(*,flags=0,first=0x7C4D50,second=0x7C4D50):
    raw=bytearray(0x48)
    pack_into("<I",raw,0x14,first)
    pack_into("<I",raw,0x28,second)
    pack_into("<I",raw,0x44,flags)
    return bytes(raw)


class Native514520ActivationTests(unittest.TestCase):
    def test_already_activated_skips_every_virtual_getter(self):
        r=source_original_514520_reached_slot_activation(
            original_node_record_at_entry=node(state=0x1234))
        self.assertEqual(r.original_branch,"already_activated_return")
        self.assertFalse(r.original_event_virtual18_called)
        self.assertFalse(r.original_first_embedded_side_v0_called)
        self.assertFalse(r.original_second_embedded_side_v0_called)
        self.assertFalse(r.native_gameplay_completion_proven)
        with self.assertRaises(OriginalNative514520SourceError):
            source_original_514520_reached_slot_activation(
                original_node_record_at_entry=node(state=1),
                original_reached_virtual18_event_pointer=0)

    def test_null_v18_short_circuits_side_getters(self):
        r=source_original_514520_reached_slot_activation(
            original_node_record_at_entry=node(),
            original_reached_virtual18_event_pointer=0)
        self.assertEqual(r.original_branch,"null_event_return")
        self.assertTrue(r.original_event_virtual18_called)
        self.assertFalse(r.original_first_embedded_side_v0_called)
        with self.assertRaises(OriginalNative514520SourceError):
            source_original_514520_reached_slot_activation(
                original_node_record_at_entry=node(),
                original_reached_virtual18_event_pointer=0,
                original_event_record_after_virtual18=event())

    def test_event_bit5_or_bit6_aborts_both_embedded_side_getters(self):
        for flags in (0x20,0x40,0x60):
            with self.subTest(flags=flags):
                r=source_original_514520_reached_slot_activation(
                    original_node_record_at_entry=node(),
                    original_reached_virtual18_event_pointer=0x2000,
                    original_event_record_after_virtual18=event(flags=flags))
                self.assertEqual(r.original_branch,
                                 "event_flags_exclude_activation")
                self.assertTrue(r.original_event_virtual18_called)
                self.assertFalse(r.original_first_embedded_side_v0_called)
                with self.assertRaises(OriginalNative514520SourceError):
                    source_original_514520_reached_slot_activation(
                        original_node_record_at_entry=node(),
                        original_reached_virtual18_event_pointer=0x2000,
                        original_event_record_after_virtual18=event(flags=flags),
                        original_reached_node_state_after_first_embedded_side_v0=0)

    def test_first_embedded_side_updates_node_skips_second(self):
        r=source_original_514520_reached_slot_activation(
            original_node_record_at_entry=node(),
            original_reached_virtual18_event_pointer=0x2000,
            original_event_record_after_virtual18=event(second=0),
            original_reached_node_state_after_first_embedded_side_v0=123)
        self.assertEqual(r.original_branch,
                         "first_side_v0_activated_node_skip_second")
        self.assertEqual(r.source_first_side_node_state_reached,123)
        self.assertTrue(r.original_first_embedded_side_v0_called)
        self.assertFalse(r.original_second_embedded_side_v0_called)
        self.assertFalse(r.native_original_world_effects_reconstructed)

    def test_first_side_zero_calls_second_only_when_real_vtable_present(self):
        r=source_original_514520_reached_slot_activation(
            original_node_record_at_entry=node(),
            original_reached_virtual18_event_pointer=0x2000,
            original_event_record_after_virtual18=event(),
            original_reached_node_state_after_first_embedded_side_v0=0)
        self.assertEqual(r.original_branch,
                         "first_side_zero_invoke_second_side_v0")
        self.assertTrue(r.original_first_embedded_side_v0_called)
        self.assertTrue(r.original_second_embedded_side_v0_called)
        self.assertFalse(r.native_original_world_effects_reconstructed)
        with self.assertRaisesRegex(OriginalNative514520SourceError,
                                    "second SideRef"):
            source_original_514520_reached_slot_activation(
                original_node_record_at_entry=node(),
                original_reached_virtual18_event_pointer=0x2000,
                original_event_record_after_virtual18=event(second=0),
                original_reached_node_state_after_first_embedded_side_v0=0)

    def test_invalid_reached_native_owners_and_results_rejected(self):
        base=dict(original_node_record_at_entry=node(),
                  original_reached_virtual18_event_pointer=0x2000,
                  original_event_record_after_virtual18=event(),
                  original_reached_node_state_after_first_embedded_side_v0=0)
        bad=(
            dict(original_node_record_at_entry=None),
            dict(original_node_record_at_entry=bytearray(node())),
            dict(original_node_record_at_entry=bytes(11)),
            dict(original_node_record_at_entry=node(vt=0)),
            dict(original_reached_virtual18_event_pointer=None),
            dict(original_reached_virtual18_event_pointer=True),
            dict(original_reached_virtual18_event_pointer=-1),
            dict(original_reached_virtual18_event_pointer=0x100000000),
            dict(original_event_record_after_virtual18=bytes(0x47)),
            dict(original_event_record_after_virtual18=bytearray(event())),
            dict(original_event_record_after_virtual18=event(first=0)),
            dict(original_reached_node_state_after_first_embedded_side_v0=None),
            dict(original_reached_node_state_after_first_embedded_side_v0=True),
            dict(original_reached_node_state_after_first_embedded_side_v0=-1),
            dict(original_reached_node_state_after_first_embedded_side_v0=0x100000000),
        )
        for variant in bad:
            with self.subTest(case=variant):
                with self.assertRaises(OriginalNative514520SourceError):
                    source_original_514520_reached_slot_activation(
                        **(base|variant))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_exact_original_514520_pe_entry_side_dispatch_and_return(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        checks=(
            (0x514520,"56 57 8b f9"),
            (0x514524,"8b 47 08 85 c0"),
            (0x51452B,"8b 07 ff 50 18"),
            (0x514536,"8b 46 44"),
            (0x51453B,"c1 e9 05 f6 c1 01"),
            (0x514543,"c1 e8 06 a8 01"),
            (0x51454A,"8b 56 14 8d 4e 14 ff 12"),
            (0x514552,"8b 47 08 85 c0"),
            (0x514559,"8b 46 28 8d 4e 28 ff 10"),
            (0x514561,"5f 5e c3"),
        )
        for addr,h in checks:
            with self.subTest(addr=hex(addr)):
                expected=bytes.fromhex(h)
                self.assertEqual(pe.read(addr,len(expected)),expected)


if __name__=="__main__":
    unittest.main()
