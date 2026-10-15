"""Guarded no-human original 5DB37C->5DB6FA context source-only test."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_match_nonhuman_stage_context_join import (
    OriginalNonhumanStageContextJoinError,source_original_5db37c_nonhuman_direct_context)

def kwargs(values=(2.9,3.9,4.9,5.9),gates=(True,)*4):
    buf=bytearray(0x70)
    for off,val in zip((0x60,0x58,0x68,0x50),values):
        pack_into('<d',buf,off,val)
    return dict(original_stage_stack_at_5db37c=bytes(buf),
                original_entered_stage_guards=gates,
                original_4037b0_human_gate_at_5db3b2=False,
                original_stack_flag_at_5db3b9=0,
                original_processing_object_pointer_at_entry=0x123400,
                original_reached_processing_pointer_at_5db70c=0x123400,
                original_context_before_5db6fa=bytes(0xda0))

class OriginalNonhumanStageContextJoinTests(TestCase):
    def test_pairs_join_true_native_context_d84_d8c_d90(self):
        r=source_original_5db37c_nonhuman_direct_context(**kwargs())
        c=r.source_context_tail
        self.assertEqual((c.first_component,c.second_component,c.source_context_d84),(6,8,14))
        self.assertEqual((c.source_context_d94,c.source_context_d98,c.source_context_d9c),(2,2,4))
        self.assertEqual(unpack_from('<III',c.native_context_after_reached_stores,0xd84),(14,0,6))
        self.assertEqual(unpack_from('<II',c.native_context_after_reached_stores,0xd90),(8,2))
        self.assertFalse(r.original_native_match_executed)
        self.assertFalse(r.live_game_state_updated)

    def test_stage_skipped_independent_guard(self):
        r=source_original_5db37c_nonhuman_direct_context(**kwargs((2.9,3.9,0.,5.9),(True,True,False,True)))
        self.assertEqual((r.source_context_tail.first_component,r.source_context_tail.second_component),(2,8))

    def test_human_zero_flag_owner_and_invalid_source_fail_closed(self):
        bad=(dict(original_4037b0_human_gate_at_5db3b2=True),
             dict(original_4037b0_human_gate_at_5db3b2=None),
             dict(original_stack_flag_at_5db3b9=1),
             dict(original_stack_flag_at_5db3b9=False),
             dict(original_reached_processing_pointer_at_5db70c=123),
             dict(original_stage_stack_at_5db37c=bytes(0x70)),
             dict(original_entered_stage_guards=(None,)*4))
        for b in bad:
            with self.subTest(bad=b):
                with self.assertRaises(ValueError):
                    source_original_5db37c_nonhuman_direct_context(**(kwargs()|b))

    def test_original_pe_branch_targets_and_context_stores(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5DB3B2:'e8 f9 83 e2 ff 84 c0 8a 44 24 0f',
            0x5DB3BD:'0f 84 0c 01 00 00',
            0x5DB4CF:'84 c0 0f 84 23 02 00 00',
            0x5DB6FA:'33 d2 89 5c 24 20 89 54 24 24 8b 4c 24 18 df 6c 24 20',
            0x5DB70C:'8b 7d 0c 8d 04 19 89 44 24 18 d9 c0 de f1',
            0x5DB71A:'89 87 84 0d 00 00 89 9f 8c 0d 00 00 89 8f 90 0d 00 00',
        }
        for va,s in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(s)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for va,target in ((0x5DB3BD,0x5DB4CF),(0x5DB4D1,0x5DB6FA)):
            p=va-0x400000
            self.assertEqual(raw[p:p+2],bytes.fromhex('0f 84'))
            self.assertEqual(va+6+unpack_from('<i',raw,p+2)[0],target)

    def test_human_5dc510_callback_has_mutable_state_and_event_queue(self):
        """Proves rejecting human path prevents omission of reached side effects."""
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5DB450:'8b 8f 70 06 00 00 e8 b5 10 00 00',
            0x5DB4B3:'8b 8f 70 06 00 00 e8 52 10 00 00',
            0x5DB4BE:'8b 8f 94 06 00 00 03 19',
            0x5DC519:'53 56 8b f1 57',
            0x5DC586:'dc 46 10',
            0x5DC599:'dd 5e 10',
            0x5DC638:'8b ce e8 31 b7 03 00',
            0x5DC63F:'5f 5e 5b 8b e5 5d c2 24 00',
        }
        for va,seq in sites.items():
            with self.subTest(callback=hex(va)):
                b=bytes.fromhex(seq)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        # Two reached human-first 5DC510 callbacks are not interchangeable
        # with the subsequently source-proven EBX += user+694 DWORD0.
        for site,target in ((0x5DB456,0x5DC510),(0x5DB4B9,0x5DC510),
                            (0x5DC63A,0x617D70)):
            p=site-0x400000
            self.assertEqual(raw[p],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,p+1)[0],target)
