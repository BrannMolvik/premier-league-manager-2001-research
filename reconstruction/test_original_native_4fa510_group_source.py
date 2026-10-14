"""Original 4FA510 group source pointer/index and private x86 byte checks."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into
from unittest import TestCase
from original_native_4fa510_group_source import (
    Original4FA510GroupSourceError,source_original_4fa510_group_category,
)

def fixture(*, slot=0, field=0x21, count=5, matches=(3,)):
    obj=bytearray(0x24)
    pack_into('<h',obj,0x20,slot)
    group=bytearray(0x6c)
    pack_into('<i',group,0x4c,count)
    native=0x30100
    if count>0:
        pack_into('<I',group,0x48,0x90000)
        members=[0x80000+i*4 for i in range(count)]
        for i in matches:
            if 0<=i<count:members[i]=native
        memberbytes=b''.join(m.to_bytes(4,'little') for m in members)
    else:memberbytes=None
    return dict(
        original_4fa510_ecx_object_pointer=native,
        original_4fa510_object_bytes=bytes(obj),
        original_global_876c50_base_pointer=0x100000,
        original_reached_876c50_index_slot_pointer=(0x100000+(slot<<6)+0x24)&0xffffffff,
        original_reached_index_slot_dword=field.to_bytes(4,'little'),
        original_global_874be0_groups_base_pointer=0x200000,
        original_reached_410ff0_group_pointer=(0x200000+field*108)&0xffffffff,
        original_reached_410ff0_group_record=bytes(group),
        original_reached_410ff0_member_array_pointer_if_positive=(0x90000 if count>0 else None),
        original_reached_410ff0_member_dwords_if_positive=memberbytes,
    )

class Original4FA510GroupSourceTests(TestCase):
    def test_original_410ff0_returns_first_matching_native_object_index(self):
        for positions,expected in (((3,),3),((2,4),2),((),0xffffffff),((0,4),0)):
            with self.subTest(positions=positions):
                source=source_original_4fa510_group_category(**fixture(matches=positions))
                self.assertEqual(source.original_4fa510_returned_eax,expected)
                self.assertEqual(source.original_group_field_at_876c50_plus24,0x21)
                self.assertFalse(source.original_native_4fa510_executed)

    def test_nonpositive_counts_return_negative_one_without_loading_pointer(self):
        for count in (-2147483648,-1,0):
            with self.subTest(count=count):
                result=source_original_4fa510_group_category(**fixture(count=count))
                self.assertEqual(result.original_4fa510_returned_eax,0xffffffff)
                self.assertEqual(result.original_410ff0_member_pointer_or_zero,0)

    def test_original_signed_20_slot_and_full_group_index(self):
        for slot,field in ((-32768,1),(-1,0),(0,0x21),(5,16),(32767,512)):
            with self.subTest(slot=slot,field=field):
                result=source_original_4fa510_group_category(**fixture(slot=slot,field=field))
                self.assertEqual(result.original_signed_20_slot,slot)
                self.assertEqual(result.original_4f8ff0_group_pointer,
                                 (0x200000+108*field)&0xffffffff)

    def test_missing_source_group_member_or_pointer_identity_fails_closed(self):
        good=fixture()
        for bad in (
            {'original_reached_876c50_index_slot_pointer':0x20004},
            {'original_reached_index_slot_dword':b''},
            {'original_global_874be0_groups_base_pointer':False},
            {'original_reached_410ff0_group_pointer':0x210000},
            {'original_reached_410ff0_group_record':bytes(20)},
            {'original_reached_410ff0_member_array_pointer_if_positive':0},
            {'original_reached_410ff0_member_dwords_if_positive':bytes(12)},
            {'original_4fa510_ecx_object_pointer':True},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original4FA510GroupSourceError):
                    source_original_4fa510_group_category(**(good|bad))
        empty=fixture(count=0)|{'original_reached_410ff0_member_dwords_if_positive':bytes(0)}
        with self.assertRaises(Original4FA510GroupSourceError):
            source_original_4fa510_group_category(**empty)

    def test_private_original_4fa510_4f8ff0_410ff0_opcode_sites(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('original executable not shipped to public CI')
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        sites={
          0x4fa510:'51',0x4fa511:'e8 da ea ff ff',0x4fa516:'8b c8',
          0x4fa518:'e8 d3 6a f1 ff',0x4fa51d:'c3',
          0x4f8ff0:'0f bf 41 20',0x4f8ff4:'8b 0d 50 6c 87 00',
          0x4f8ffa:'c1 e0 06',0x4f8ffd:'8b 44 08 24',
          0x4f9001:'8d 04 40',0x4f9004:'8d 14 c0',
          0x4f9007:'a1 e0 4b 87 00',0x4f900c:'8d 04 90',
          0x410ff0:'8b 51 4c',0x410ff3:'33 c0',0x410ff6:'85 d2',
          0x410ff8:'7e 13',0x410ffa:'8b 49 48',
          0x410ffd:'8b 74 24 08',0x411001:'3b 31',
          0x411003:'74 0b',0x411005:'40',0x411006:'83 c1 04',
          0x411009:'3b c2',0x41100b:'7c f4',
          0x41100d:'83 c8 ff',0x411011:'c2 04 00',
        }
        for va,dump in sites.items():
            with self.subTest(address=hex(va)):
                raw=bytes.fromhex(dump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(raw)],raw)
