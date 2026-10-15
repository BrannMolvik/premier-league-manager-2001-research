"""Native 4056D0->4056F0->4F3B10 signed bucket linked path tests."""
from dataclasses import replace
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into
from unittest import TestCase
from original_native_40cbc0_coeff_route import (
    source_original_5da967_40cbc0_club_coefficient_route,
    source_original_40cbc0_4056d0_club_query_word,
)
from original_native_4f3b10_query_owner import (
    Original4F3B10QuerySourceError, SourceOriginal4F3B10NativeNode,
    source_original_4f3b10_reached_query_owner,
)

def query(key=0x1234):
    club=bytearray(0x18)
    pack_into("<I",club,0x10,key)
    pack_into("<I",club,0x14,24)
    reached=dict(original_5da967_first_side_club_pointer=0x70000,
                 original_40cbc0_ecx_club_pointer=0x70000,
                 original_40cbc0_club_record=bytes(club))
    route=source_original_5da967_40cbc0_club_coefficient_route(**reached)
    return source_original_40cbc0_4056d0_club_query_word(
        original_route=route,
        original_40cbc0_club_record_at_query=bytes(club),
        original_4056d0_ecx_club_pointer_at_call=0x70000)

def node(ptr,key=0,nextptr=0):
    record=bytearray(0x24)
    pack_into("<I",record,0x10,nextptr)
    pack_into("<H",record,0x22,key)
    return SourceOriginal4F3B10NativeNode(ptr,bytes(record))

def indexed():
    obj=query()
    return dict(
        original_4056d0_query_receipt=obj,
        original_global_876c44_bucket_array_pointer_if_indexed=0x100000,
        original_reached_876c44_index_slot_pointer_if_indexed=0x100000+0x1234*4,
        original_reached_index_bucket_pointer_record_if_indexed=(0x30000).to_bytes(4,"little"),
        original_global_876bc8_sentinel_head_pointer_if_sentinel=None,
        original_native_list_nodes_in_order=(node(0x30000,1,0x30100),node(0x30100)),
    )

class SourceOriginal4F3B10QueryTests(TestCase):
    def test_indexed_bucket_walk_selects_original_first_matching_subkey(self):
        out=source_original_4f3b10_reached_query_owner(**indexed())
        self.assertEqual(out.original_query_word,0x1234)
        self.assertEqual(out.original_query_subkey_word,0)
        self.assertEqual(out.original_walked_pointer_order,(0x30000,0x30100))
        self.assertEqual(out.original_found_object_pointer_or_zero,0x30100)
        self.assertFalse(out.original_4fa520_executed)

    def test_sentinel_ffff_uses_876bc8_and_not_index_table(self):
        state=indexed()
        state.update(original_4056d0_query_receipt=query(0xffff),
            original_global_876c44_bucket_array_pointer_if_indexed=None,
            original_reached_876c44_index_slot_pointer_if_indexed=None,
            original_reached_index_bucket_pointer_record_if_indexed=None,
            original_global_876bc8_sentinel_head_pointer_if_sentinel=0x40000,
            original_native_list_nodes_in_order=(node(0x40000),))
        out=source_original_4f3b10_reached_query_owner(**state)
        self.assertEqual(out.original_found_object_pointer_or_zero,0x40000)
        self.assertEqual(out.original_query_word,0xffff)

    def test_negative_signed_key_and_empty_or_nonmatching_head(self):
        state=indexed()
        key=0x8000
        base=0x100000
        state.update(original_4056d0_query_receipt=query(key),
            original_reached_876c44_index_slot_pointer_if_indexed=(base-32768*4)&0xffffffff,
            original_reached_index_bucket_pointer_record_if_indexed=bytes(4),
            original_native_list_nodes_in_order=())
        out=source_original_4f3b10_reached_query_owner(**state)
        self.assertEqual(out.original_found_object_pointer_or_zero,0)
        state['original_reached_index_bucket_pointer_record_if_indexed']=(0x30000).to_bytes(4,"little")
        state['original_native_list_nodes_in_order']=(node(0x30000,key=44),)
        out=source_original_4f3b10_reached_query_owner(**state)
        self.assertEqual(out.original_walked_pointer_order,(0x30000,))
        self.assertEqual(out.original_found_object_pointer_or_zero,0)

    def test_early_match_rejects_unreached_nodes_and_ended_chain_fails_closed(self):
        state=indexed()
        for changed in (
            {'original_native_list_nodes_in_order':(node(0x30000),node(0x30100))},
            {'original_native_list_nodes_in_order':(node(0x30000,1,0x30100),)},
            {'original_native_list_nodes_in_order':(node(0x30000,1,0x30000),node(0x30000))},
            {'original_native_list_nodes_in_order':(node(0x30000,1,0x30100),node(0x99999))},
            {'original_reached_876c44_index_slot_pointer_if_indexed':0x100000},
            {'original_reached_index_bucket_pointer_record_if_indexed':bytes(2)},
            {'original_global_876bc8_sentinel_head_pointer_if_sentinel':0x40000},
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(Original4F3B10QuerySourceError):
                    source_original_4f3b10_reached_query_owner(**(state|changed))

    def test_optional_original_pe_indexed_and_linked_opcode_sites(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("original executable stays private, not hosted in CI")
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        sites={0x4056f0:"8b 44 24 04",0x4056f5:"e8 16 e4 0e 00",
            0x4f3b10:"8b 44 24 04",0x4f3b14:"66 3d ff ff",
            0x4f3b1a:"a1 c8 6b 87 00",
            0x4f3b21:"8b 0d 44 6c 87 00",
            0x4f3b27:"0f bf c0",0x4f3b2a:"8b 04 81",
            0x4f3b31:"66 8b 4c 24 06",
            0x4f3b36:"66 39 48 22",
            0x4f3b3c:"8b 40 10",
            0x4f3b43:"33 c0",0x4f3b45:"c3"}
        for va,dump in sites.items():
            with self.subTest(va=hex(va)):
                exp=bytes.fromhex(dump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(exp)],exp)
