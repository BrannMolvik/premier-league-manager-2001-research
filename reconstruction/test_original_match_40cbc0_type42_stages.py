"""Original 40CBC0 club type42 four-stage QWORD outputs from source native PE."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_match_40cbc0_type42_stages import (
    OriginalMatch40CBC0Type42Error,
    source_original_40cbc0_team_type42_output_pair as project,
)


def inputs(*,enums=(0,2,2,6),kind=0x42):
    team=bytearray(0x18)
    pack_into('<I',team,0x10,0x123456)
    pack_into('<I',team,0x14,kind)
    return dict(original_team_pointer=0x4000,
        original_team_record=bytes(team),
        original_reached_4056d0_source_key_pointer=0x123456,
        original_reached_four_4fa520_selector_dwords=enums)


class Original40CBC0Type42StagesTests(TestCase):
    def test_only_first_native_stage_assigns_20_16_12_9_when_others_skip(self):
        for i,expected in enumerate((20.,16.,12.,9.,9.)):
            with self.subTest(i=i):
                r=project(**inputs(enums=(i,0xffffffff,3,6)))
                self.assertEqual((r.first_original_qword_output,
                                  r.second_original_qword_output,
                                  r.original_last_write_stage),(expected,expected*.75,0))
                self.assertFalse(r.original_match_state_written)

    def test_source_second_and_third_selected_enum_overwrite_previous_pair(self):
        for stage,enum,expected in ((1,0,15.),(1,1,10.),(2,0,17.),(2,1,12.)):
            seq=[0,6,6,6]
            seq[stage]=enum
            with self.subTest(stage=stage,enum=enum):
                r=project(**inputs(enums=tuple(seq)))
                self.assertEqual((r.first_original_qword_output,
                                  r.second_original_qword_output,r.original_last_write_stage),
                                 (expected,expected*.75,stage))

    def test_source_final_fourth_stage_overrides_with_half_base_and_three_quarters(self):
        for enum,expected in enumerate((15.,10.,8.,6.,4.5)):
            with self.subTest(enum=enum):
                r=project(**inputs(enums=(0,0,0,enum)))
                self.assertEqual((r.first_original_qword_output,
                                  r.second_original_qword_output,r.original_last_write_stage),
                                 (expected,expected*.75,3))

    def test_four_absent_enums_leave_actual_original_5da8d9_initialized_qword_zero(self):
        r=project(**inputs(enums=(5,6,0xffffffff,5)))
        self.assertEqual((r.first_original_qword_output,
                          r.second_original_qword_output,r.original_last_write_stage),
                         (0.,0.,None))
        self.assertFalse(r.original_native_40cbc0_executed)
        self.assertFalse(r.original_4056d0_4fa520_callbacks_executed)

    def test_reject_wrong_club_type_key_or_malformed_source_receipts(self):
        good=inputs()
        changes=(
            {'original_team_pointer':0},
            {'original_team_pointer':True},
            {'original_team_record':bytes(0x18)},
            {'original_team_record':b''},
            {'original_team_record':bytearray(0x18)},
            {'original_reached_4056d0_source_key_pointer':0},
            {'original_reached_4056d0_source_key_pointer':True},
            {'original_reached_four_4fa520_selector_dwords':(1,)},
            {'original_reached_four_4fa520_selector_dwords':[0,1,2,3]},
            {'original_reached_four_4fa520_selector_dwords':(0,1,True,3)},
            {'original_reached_four_4fa520_selector_dwords':(0,1,2,-1)},
            {'original_preexisting_first_qword':1.0},
            {'original_preexisting_second_qword':0.5},
        )
        for changed in changes:
            with self.subTest(changed=changed),self.assertRaises(OriginalMatch40CBC0Type42Error):
                project(**(good|changed))
        with self.assertRaises(OriginalMatch40CBC0Type42Error):
            project(**inputs(kind=0x1a))

    def test_original_pe_type42_branch_jump_selector_stage_and_native_double_constants(self):
        name=environ.get('FM2001_ORIGINAL_EXE')
        if not name:self.skipTest('original private executable unavailable in CI')
        raw=Path(name).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x40ce09:'8b 57 10',
            0x40ce24:'e8 f7 d6 0e 00',
            0x40ce2b:'83 f8 04',
            0x40ce30:'ff 24 85 08 d0 40 00',
            0x40ce37:'a1 90 20 82 00',
            0x40ce44:'8b 15 a0 20 82 00',
            0x40ce56:'8b 0d b0 20 82 00',
            0x40ce69:'a1 c0 20 82 00',
            0x40ce83:'8b 47 10',
            0x40cea3:'8b 00',
            0x40ceda:'8b 47 10',
            0x40cf31:'8b 47 10',
            0x40cf58:'ff 24 85 1c d0 40 00',
            0x40cf85:'dc 0d a8 d6 7b 00',
            0x40cf8d:'dc 0d 58 d5 7b 00',
        }
        for va,hexbytes in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(hexbytes)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        self.assertEqual(raw[0x40cfc0-0x400000+(0x42-0x18)],5)
        self.assertEqual(unpack_from('<I',raw,0x40cfa0-0x400000+5*4)[0],0x40ce09)
        self.assertEqual(tuple(unpack_from('<I',raw,0x40d008-0x400000+i*4)[0]
                        for i in range(5)),
                        (0x40ce37,0x40ce44,0x40ce56,0x40ce69,0x40ce69))
        self.assertEqual(tuple(unpack_from('<d',raw,va-0x400000)[0]
                         for va in (0x822090,0x8220a0,0x8220b0,0x8220c0)),
                         (20.,16.,12.,9.))
        self.assertEqual((unpack_from('<d',raw,0x7bd6a8-0x400000)[0],
                          unpack_from('<d',raw,0x7bd558-0x400000)[0]),(.5,.75))
