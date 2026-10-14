"""Original 668350 signed FISTP and 5DB4C4 human owner, source only."""
from struct import pack
from unittest import TestCase,main
from original_native_5db389_component_inputs import (
    OriginalNativeComponentInputError,source_original_5db389_four_float_components,
)

def fixture(a=13.9,b=20.8,c=10.4,d=7.6,human=None):
    return dict(
        original_5db37c_esp68_qword=pack('<d',a),
        original_5db385_esp60_qword=pack('<d',b),
        original_5db390_esp50_qword=pack('<d',c),
        original_5db39f_esp58_qword=pack('<d',d),
        original_5db4c4_human_reached=human is not None,
        original_user_694_owner_pointer_if_reached=0x30000 if human is not None else None,
        original_reached_user_694_record_if_reached=human.to_bytes(4,'little') if human is not None else None,
    )

class SourceOriginalComponentInputTests(TestCase):
    def test_four_source_fpu_truncations_and_human_addend_are_separate(self):
        a=source_original_5db389_four_float_components(**fixture())
        self.assertEqual(a.native_low32_conversion_results,(13,20,10,7))
        self.assertEqual((a.original_ebx_at_5db6fa,a.original_ecx_at_5db704),(33,17))
        b=source_original_5db389_four_float_components(**fixture(human=9))
        self.assertEqual((b.original_ebx_at_5db396,b.original_ebx_at_5db6fa,b.original_ecx_at_5db704),
                         (33,42,17))
        self.assertFalse(b.original_668350_callbacks_executed)

    def test_negative_source_truncates_to_zero_and_wraps_low32(self):
        out=source_original_5db389_four_float_components(**fixture(-3.9,2.1,1,1,human=3))
        self.assertEqual(out.native_low32_conversion_results[0],0xfffffffd)
        self.assertEqual((out.original_ebx_at_5db396,out.original_ebx_at_5db6fa),
                         (0xffffffff,2))

    def test_missing_source_or_fpu_invalid_inputs_fail_closed(self):
        base=fixture()
        for bad in (
            {'original_5db37c_esp68_qword':b''},
            {'original_5db37c_esp68_qword':pack('<d',float('nan'))},
            {'original_5db37c_esp68_qword':pack('<d',float('inf'))},
            {'original_5db37c_esp68_qword':pack('<d',1e33)},
            {'original_5db4c4_human_reached':1},
            {'original_reached_user_694_record_if_reached':bytes(4)},
            {'original_5db4c4_human_reached':True},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalNativeComponentInputError):
                    source_original_5db389_four_float_components(**(base|bad))
if __name__=='__main__':main()
