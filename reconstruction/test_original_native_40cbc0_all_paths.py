"""Original 40CBC0 all native dispatches, per-call category and QWORD stores."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_40cbc0_coeff_route import source_original_5da967_40cbc0_club_coefficient_route
from original_native_40cbc0_full_category_join import source_original_40cbc0_full_linked_category
from original_native_40cbc0_all_paths import (
    Original40CBC0AllPathSourceError, source_original_40cbc0_all_dispatch_coefficients,
)
from test_original_native_40cbc0_full_category_join import reached

# Independent branch-start/call-count oracle from source CFG, not code constants.
START_AND_CALLS={24:(0x40ce83,3),26:(0x40cbf2,1),31:(0x40ceda,2),
                 33:(0x40ccc9,1),40:(0x40cd5d,6),66:(0x40ce09,4),
                 73:(0x40cdb3,5),25:(0x40cf31,1)}

def stage(kind,category):
    source=reached(matches=(category,) if category<=4 else ())
    chain=source['original_40cbc0_reached_query_category_inputs']
    dispatch=chain['original_40cbc0_dispatch_input']
    club=bytearray(dispatch['original_40cbc0_club_record'])
    pack_into('<I',club,0x14,kind)
    next_dispatch=dispatch|{'original_40cbc0_club_record':bytes(club)}
    new_route=source_original_5da967_40cbc0_club_coefficient_route(**next_dispatch)
    chain['original_40cbc0_dispatch_input']=next_dispatch
    chain['original_4056d0_query_input']=chain['original_4056d0_query_input']|{
         'original_route':new_route,'original_40cbc0_club_record_at_query':bytes(club)}
    group=source['original_4fa510_group_source_inputs']
    group['original_reached_index_slot_dword']=(0x20).to_bytes(4,'little')
    group['original_reached_410ff0_group_pointer']=0x200000+0x20*108
    cat=chain['original_4fa520_category_input']
    cat['original_reached_slot_dword_record']=(0x20).to_bytes(4,'little')
    cat['original_4fa510_returned_eax']=category if category<=4 else 0xffffffff
    return source_original_40cbc0_full_linked_category(**source)

def call(kind,category):
    category_value=category if category<=4 else 0xffffffff
    return dict(
      original_first_native_category_receipt=stage(kind,category),
      original_actual_categories_for_each_4fa520_call=tuple(
          [category_value]*START_AND_CALLS[kind][1]),
      original_ebp8_first_qword_pointer=0x50000,
      original_ebpc_second_qword_pointer=0x50100,
      original_first_qword_before=bytes([0xab])*8,
      original_second_qword_before=bytes([0xcd])*8,
    )

class Original40CBC0WholeBranchTests(TestCase):
    def test_all_eight_dispatch_paths_source_category_five_pairs_and_skip(self):
        bases=(30.,20.,16.,12.,9.)
        for kind,(target,count) in START_AND_CALLS.items():
            for category in (0,1,2,3,4,0xffffffff):
                with self.subTest(kind=kind,category=category):
                    result=source_original_40cbc0_all_dispatch_coefficients(**call(kind,category))
                    self.assertEqual(result.original_entry_target,target)
                    self.assertEqual(result.original_reached_category_calls,count)
                    if category==0xffffffff or (kind==33 and category>2):
                        self.assertFalse(result.original_any_coefficient_written)
                        self.assertEqual(result.original_first_qword_after,bytes([0xab])*8)
                        self.assertEqual(result.original_second_qword_after,bytes([0xcd])*8)
                    else:
                        expected=(bases[category] if kind==26 else
                                  (20.,15.,10.)[category] if kind==33 else
                                  bases[category]*0.5)
                        self.assertEqual(unpack_from('<d',result.original_first_qword_after)[0],expected)
                        self.assertEqual(unpack_from('<d',result.original_second_qword_after)[0],
                                         expected*0.75)
                        self.assertTrue(result.original_any_coefficient_written)
                    self.assertFalse(result.original_40cbc0_executed)
                    self.assertFalse(result.live_game_state_updated)

    def test_original_fallthrough_emits_preceding_side_effecting_qword_writes(self):
        expected={
            24:(0x40ce83,0x40ceda,0x40cf31),
            31:(0x40ceda,0x40cf31),
            40:(0x40cd5d,0x40cdb3,0x40ce09,0x40ce83,0x40ceda,0x40cf31),
            66:(0x40ce09,0x40ce83,0x40ceda,0x40cf31),
            73:(0x40cdb3,0x40ce09,0x40ce83,0x40ceda,0x40cf31),
        }
        for kind,addresses in expected.items():
            with self.subTest(kind=kind):
                result=source_original_40cbc0_all_dispatch_coefficients(**call(kind,0))
                self.assertEqual(tuple(x.native_branch_entry_va for x in result.original_intermediate_output_store_order),
                                 addresses)
                self.assertEqual(result.original_first_qword_after,
                                 result.original_intermediate_output_store_order[-1].source_first_qword_after)
        # For category 2, intermediate case40/73/24/31 don't write.
        result=source_original_40cbc0_all_dispatch_coefficients(**call(40,2))
        self.assertEqual(tuple(x.native_branch_entry_va for x in result.original_intermediate_output_store_order),
                         (0x40ce09,0x40cf31))

    def test_native_category_call_count_and_value_drift_are_not_collapsed(self):
        state=call(40,2)
        for altered in (
            {'original_actual_categories_for_each_4fa520_call':(2,)},
            {'original_actual_categories_for_each_4fa520_call':(2,2,2,2,2,3)},
            {'original_actual_categories_for_each_4fa520_call':(2,2,2,2,2,True)},
            {'original_actual_categories_for_each_4fa520_call':[2]*6},
            {'original_ebp8_first_qword_pointer':0},
            {'original_ebpc_second_qword_pointer':0x50000},
            {'original_first_qword_before':bytes(4)},
        ):
            with self.subTest(altered=altered):
                with self.assertRaises(Original40CBC0AllPathSourceError):
                    source_original_40cbc0_all_dispatch_coefficients(**(state|altered))

    def test_original_pe_const_values_and_source_fallthrough_native_opcodes(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('canonical original remains private, not in hosted CI')
        pe=Path(path).read_bytes()
        self.assertEqual(sha256(pe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        constants={0x822040:30.,0x822050:20.,0x822060:16.,0x822070:12.,
            0x822080:9.,0x822090:20.,0x8220a0:16.,0x8220b0:12.,
            0x8220c0:9.,0x8220d0:25.,0x8220e0:17.,
            0x822110:20.,0x822120:15.,0x822130:10.,
            0x822140:15.,0x822150:10.,0x822160:17.,0x822170:12.}
        for va,val in constants.items():
            with self.subTest(constant=hex(va)):
                self.assertEqual(unpack_from('<d',pe,va-0x400000)[0],val)
        self.assertEqual(unpack_from('<d',pe,0x7bd558-0x400000)[0],0.75)
        jump=tuple(unpack_from('<I',pe,0x40d008-0x400000+i*4)[0] for i in range(5))
        self.assertEqual(jump,(0x40ce37,0x40ce44,0x40ce56,0x40ce69,0x40ce69))
        sites={
            0x40cc14:'83 f8 04',0x40cc3c:'5f 5e 5b',
            0x40ccc9:'8b 57 10',0x40ccf4:'0f 85 9b 02 00 00',
            0x40cd5d:'8b 57 10',0x40cdb1:'dd 1b',0x40cdb3:'8b 57 10',
            0x40ce09:'8b 57 10',0x40ce2e:'77 53',
            0x40ce81:'dd 1b',0x40ce83:'8b 47 10',
            0x40ced8:'dd 1b',0x40ceda:'8b 47 10',
            0x40cf2f:'dd 1b',0x40cf31:'8b 47 10',
            0x40cf53:'83 f8 04',0x40cf95:'5f 5e 5b',
        }
        for va,encoded in sites.items():
            with self.subTest(original_va=hex(va)):
                raw=bytes.fromhex(encoded)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(raw)],raw)
