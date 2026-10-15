"""Original PResults PostponedEvent wrapper delegates v+0C/+18, not event+8."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into, unpack_from
from unittest import TestCase

from original_presults_native_event_work import OriginalPResultsEventSourceError
from original_presults_postponed_wrapper_precount import (
    source_original_postponed_wrapper_precount_node_4a7210 as source,
)


def records(*,under_flags=0, wrapper_link=0, before_match_flags=None,
            wrapper_pointer=0x9000, old_event_pointer=0x3000,
            under_vtable=0x7c4c24, first=0x1111,second=0x2222):
    before=bytearray(0x58)
    pack_into('<I',before,0,under_vtable)
    pack_into('<I',before,8,wrapper_pointer)
    pack_into('<I',before,0x44,under_flags if before_match_flags is None else before_match_flags)
    after=bytearray(before)
    pack_into('<I',after,0x44,under_flags)
    wrapper=bytearray(0x1c)
    pack_into('<I',wrapper,0,0x7c9fe8)
    pack_into('<I',wrapper,8,wrapper_link)
    pack_into('<I',wrapper,0x14,old_event_pointer)
    kwargs=dict(
        original_wrapper_event_pointer=wrapper_pointer,
        original_wrapper_record_before_v0c=bytes(wrapper),
        original_underlying_match_event_pointer=old_event_pointer,
        original_underlying_match_record_before_v0c=bytes(before),
        original_first_club_virtual_result_pointer=first,
        original_second_club_virtual_result_pointer=second,
        original_special_owner_record_via_plus54=None,
        original_wrapper_record_after_reached_v0c=bytes(wrapper),
        original_underlying_match_record_after_reached_v0c=bytes(after),
    )
    return kwargs


class OriginalPostponedWrapperPResultsTests(TestCase):
    def test_new_wrapper_8_zero_counts_source_underlying_flags_despite_old_8_link(self):
        v=records()
        r=source(**v)
        self.assertEqual(r.original_event_pointer,0x9000)
        self.assertTrue(r.source_virtual_0c_nonzero)
        self.assertEqual(r.reached_event8,0)
        self.assertEqual(r.reached_payload44,0)
        self.assertEqual(unpack_from('<I',v['original_underlying_match_record_before_v0c'],8)[0],0x9000)

    def test_linked_new_wrapper_not_counted_even_if_underlying_would_be_eligible(self):
        v=records(wrapper_link=0x9100,under_flags=0)
        r=source(**v)
        self.assertTrue(r.source_virtual_0c_nonzero)
        self.assertEqual(r.reached_event8,0x9100)
        self.assertIsNone(r.reached_payload44)

    def test_underlying_bit5_virtual_false_skips_wrapper_state_inspection(self):
        v=records(under_flags=0x20)
        v['original_first_club_virtual_result_pointer']=None
        v['original_second_club_virtual_result_pointer']=None
        v['original_underlying_match_record_after_reached_v0c']=None
        v['original_wrapper_record_after_reached_v0c']=None
        r=source(**v)
        self.assertFalse(r.source_virtual_0c_nonzero)
        self.assertIsNone(r.reached_event8)
        v['original_wrapper_record_after_reached_v0c']=bytes(0x1c)
        with self.assertRaises(OriginalPResultsEventSourceError):
            source(**v)

    def test_actual_source_payload_bit6_filters_though_original_wrapper_has_zero_link(self):
        for flags in (0x01,0x40,0x41):
            r=source(**records(under_flags=flags))
            self.assertEqual(r.reached_payload44,flags)
            self.assertTrue(r.source_virtual_0c_nonzero)

    def test_reject_wrong_vtable_underlying_link_unreached_or_guess(self):
        good=records()
        def mutable(key):
            return bytearray(good[key])
        wrong=mutable('original_wrapper_record_before_v0c')
        pack_into('<I',wrong,0,0x7c4c24)
        old=mutable('original_underlying_match_record_before_v0c')
        pack_into('<I',old,8,0)
        after=mutable('original_wrapper_record_after_reached_v0c')
        pack_into('<I',after,0x14,0x3001)
        bads=[
            dict(original_wrapper_record_before_v0c=bytes(wrong)),
            dict(original_underlying_match_record_before_v0c=bytes(old)),
            dict(original_wrapper_record_after_reached_v0c=bytes(after)),
            dict(original_wrapper_event_pointer=0),
            dict(original_underlying_match_event_pointer=0x9000),
            dict(original_underlying_match_record_after_reached_v0c=None),
            dict(original_wrapper_record_after_reached_v0c=None),
            dict(original_first_club_virtual_result_pointer=None),
        ]
        for change in bads:
            with self.subTest(changed=change.keys()),self.assertRaises(OriginalPResultsEventSourceError):
                source(**(good|change))

    def test_original_pe_510ba0_wrapper_creation_and_5140b0_vtable_delegate_sites(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original executable not available')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
             '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x510ba3:'8b 47 08 85 c0',
            0x510baf:'8b 48 44 c1 e9 06',
            0x510bde:'89 7e 14 89 56 18',
            0x510be4:'c7 06 e8 9f 7c 00',
            0x510bf8:'89 77 08',
            0x5140b0:'8b 49 14 8b 01 ff 60 0c',
            0x5140f0:'8b 49 14 8b 01 ff 60 10',
            0x514100:'8b 49 14 8b 01 ff 60 18',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        # PE .rdata native owner vtable at VA7C9FE8 maps to original raw
        # section offset 0x3C9FE8; exact virtual entry pointers at +0C/+10/+18.
        pos=0x3c9fe8
        self.assertEqual(tuple(unpack_from('<I',raw,pos+offset)[0]
                        for offset in (0x0c,0x10,0x18)),
                        (0x5140b0,0x5140f0,0x514100))
