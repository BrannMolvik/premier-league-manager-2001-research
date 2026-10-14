"""Source nonzero 5DB6FA context and original PE validation; no native execution."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase,main
from original_native_5db6fa_context_tail import (
    OriginalContextTailSourceError,source_original_5db6fa_two_component_context_tail,
)
def fixture(a=45,b=55):
    return dict(original_processing_object_pointer_at_entry=0x40000,
        original_reached_processing_pointer_at_5db70c=0x40000,
        original_context_before_5db6fa=bytes([0xa0])*0xda0,
        original_ebx_component_at_5db6fc=a,original_ecx_component_at_5db704=b)
class OriginalContextTailSourceTests(TestCase):
    def test_reached_original_two_components_and_classification_fields(self):
        data=fixture()
        result=source_original_5db6fa_two_component_context_tail(**data)
        self.assertEqual([unpack_from('<I',result.native_context_after_reached_stores,n)[0]
                          for n in (0xd84,0xd8c,0xd90,0xd94,0xd98,0xd9c)],
                         [100,45,55,2,2,4])
        self.assertFalse(result.original_native_calculator_executed)
        self.assertFalse(result.live_game_state_updated)
        self.assertEqual(data['original_context_before_5db6fa'],bytes([0xa0])*0xda0)

    def test_source_rejects_zero_negative_forged_pointer_or_short_context(self):
        base=fixture()
        for bad in (
            {'original_ebx_component_at_5db6fc':0},
            {'original_ecx_component_at_5db704':0},
            {'original_ebx_component_at_5db6fc':-1},
            {'original_ebx_component_at_5db6fc':True},
            {'original_processing_object_pointer_at_entry':0},
            {'original_reached_processing_pointer_at_5db70c':0x50000},
            {'original_context_before_5db6fa':bytes(10)},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalContextTailSourceError):
                    source_original_5db6fa_two_component_context_tail(**(base|bad))

    def test_unsigned_native_wrapping_components(self):
        result=source_original_5db6fa_two_component_context_tail(**fixture(0xffffffff,2))
        self.assertEqual(result.source_context_d84,1)
        self.assertEqual(result.source_context_d9c,4)

    def test_optional_original_binary_static_opcode_contract(self):
        file=environ.get('FM2001_ORIGINAL_EXE')
        if not file:self.skipTest('private executable not included in CI')
        pe=Path(file).read_bytes()
        self.assertEqual(sha256(pe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        sig={
            0x5db6fa:'33 d2',0x5db704:'8b 4c 24 18',
            0x5db708:'df 6c 24 20',0x5db70f:'8d 04 19',
            0x5db716:'d9 c0',0x5db718:'de f1',
            0x5db71a:'89 87 84 0d 00 00',
            0x5db720:'89 9f 8c 0d 00 00',
            0x5db726:'89 8f 90 0d 00 00',
            0x5db72c:'dc 15 18 11 82 00',
            0x5db743:'dc 1d 28 11 82 00',
            0x5db75c:'c7 87 94 0d 00 00 02 00 00 00',
            0x5db76e:'df 6c 24 20',0x5db774:'de f1',
            0x5db7a6:'c7 87 98 0d 00 00 02 00 00 00',
            0x5db7be:'e8 1d 06 00 00',
            0x5db7c3:'89 87 9c 0d 00 00',
            0x5dbde8:'03 c1',0x5dbdea:'d1 e8',
            0x5dbdec:'83 c0 02',0x5dbdef:'83 f8 04',
        }
        for va,dump in sig.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(dump)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(expected)],expected)
if __name__=='__main__':main()
