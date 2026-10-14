"""Bounded original 4FA520 signed owner slot/category source regressions."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into
from unittest import TestCase
from original_native_4fa520_category_source import (
    Original4FA520SourceError,source_original_4fa520_signed_slot_category,
)

def native(category=3, *, slot=0, field=0x21):
    record=bytearray(0x22)
    pack_into('<h',record,0x20,slot)
    base=0x100000
    ptr=(base+((slot<<6)&0xffffffff)+0x24)&0xffffffff
    return dict(
        original_4fa520_ecx_object_pointer=0x90000,
        original_4fa520_object_record=bytes(record),
        original_global_876c50_base_pointer=base,
        original_reached_slot_pointer=ptr,
        original_reached_slot_dword_record=field.to_bytes(4,'little'),
        original_4fa510_returned_eax=category,
    )

class SourceOriginal4FA520CategoryTests(TestCase):
    def test_exceptional_field_33_remaps_only_category_three_and_four(self):
        for category,expected in ((0,0),(1,1),(2,2),(3,2),(4,3),(5,5),(0xffffffff,0xffffffff)):
            with self.subTest(category=category):
                out=source_original_4fa520_signed_slot_category(**native(category=category))
                self.assertEqual(out.original_4fa520_returned_category,expected)
                self.assertFalse(out.original_4fa520_executed)

    def test_all_other_field_values_keep_original_4fa510_category(self):
        for field in (0,1,0x20,0x22,0xffffffff):
            for category in (2,3,4):
                with self.subTest(field=field,category=category):
                    out=source_original_4fa520_signed_slot_category(**native(category=category,field=field))
                    self.assertEqual(out.original_4fa520_returned_category,category)

    def test_signed_word_address_uses_original_32bit_native_arithmetic(self):
        for signed in (-32768,-100,-1,0,1,100,32767):
            with self.subTest(signed=signed):
                out=source_original_4fa520_signed_slot_category(**native(slot=signed))
                expected=(0x100000+(signed<<6)+0x24)&0xffffffff
                self.assertEqual(out.original_reached_source_slot_pointer,expected)
                self.assertEqual(out.original_signed_object_20_slot,signed)

    def test_unreached_registry_credential_and_memory_drift_fail_closed(self):
        good=native()
        for bad in ({'original_4fa520_ecx_object_pointer':0},
                    {'original_global_876c50_base_pointer':True},
                    {'original_reached_slot_pointer':0x10004},
                    {'original_4fa520_object_record':bytes(32)},
                    {'original_reached_slot_dword_record':bytes(3)},
                    {'original_4fa510_returned_eax':-1},
                    {'original_4fa510_returned_eax':True}):
            with self.subTest(bad=bad):
                with self.assertRaises(Original4FA520SourceError):
                    source_original_4fa520_signed_slot_category(**(good|bad))

    def test_private_original_4fa520_opcode_and_reachability_contract(self):
        file=environ.get('FM2001_ORIGINAL_EXE')
        if not file:self.skipTest('original executable intentionally omitted from public CI')
        exe=Path(file).read_bytes()
        self.assertEqual((len(exe),sha256(exe).hexdigest()),
            (4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={0x4fa520:'56 8b f1',0x4fa523:'e8 e8 ff ff ff',
               0x4fa528:'8b 15 50 6c 87 00',0x4fa530:'0f bf 46 20',
               0x4fa534:'c1 e0 06',0x4fa537:'8b 74 10 24',
               0x4fa53b:'83 fe 21',0x4fa543:'83 e8 03',
               0x4fa54f:'c7 00 03 00 00 00',
               0x4fa55c:'c7 00 02 00 00 00',0x4fa569:'89 08'}
        for va,opcode in sites.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(opcode)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)
