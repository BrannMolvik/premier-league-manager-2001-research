"""Original native row-state byte proofs, not original/Win11 execution."""
import os
from pathlib import Path
from struct import pack_into, unpack_from
import unittest
from original_fastview_native_player_roster_stage import (
    SourceFastViewNativePlayerRowInput,
    SourceFastViewNativePlayerRosterError,
    source_fastview_native_side_roster_stage_533370,
)


def sample(side=0, count=12):
    match = bytearray(b"\x00"*0xB58)
    pack_into('<I', match, (0x5A4,0xB54)[side], count)
    rows=[]
    for i in range(count):
        rec=bytearray(b"\x00"*0x24C)
        pack_into('<H',rec,4,400+i)
        pack_into('<I',rec,0x14,0x800 if i%2 else 0)
        pack_into('<H',rec,0x6e,300+i)
        rec[0x40:0x45]=bytes([10+i,20+i,30+i,40+i,50+i])
        rec[0x70]=60+i
        sub=bytes([1+i,2+i,3+i])
        rows.append(SourceFastViewNativePlayerRowInput(bytes(rec),sub,
                           (f'Player{i}'.encode()+b'\0'),bytes([80+i])))
        base=(0x7C,0x62C)[side]+i*0x4C
        match[base]=[0,1,5,16,255][i%5]
        for j in range(8): match[base+5+j]=0 if j%2==0 else 255
    before=bytes([0xB6])*1556
    return dict(original_side_after_533480_header=before,
                original_match_object=bytes(match), original_side_index=side,
                original_ordered_player_rows=tuple(rows),original_533ab0_result=11)


class OriginalFastViewNativeRosterTests(unittest.TestCase):
    def test_two_distinct_sides_72_byte_row_and_8_status_values(self):
        for side in (0,1):
            args=sample(side=side,count=12+side)
            out=source_fastview_native_side_roster_stage_533370(**args)
            self.assertEqual(len(out),1556)
            self.assertEqual(unpack_from('<I',out,0xFC)[0],12+side)
            self.assertEqual(unpack_from('<I',out,0x100)[0],11)
            self.assertEqual(out[0:0xFC],b'\xB6'*0xFC)
            for i in range(12+side):
                at=0x104+i*0x48
                self.assertEqual(out[at:at+len(f'Player{i}')+1],f'Player{i}'.encode()+b'\0')
                self.assertEqual(out[at+0x20],80+i)
                self.assertEqual(unpack_from('<I',out,at+0x24)[0],400+i)
                self.assertEqual(unpack_from('<I',out,at+0x28)[0],300+i)
                self.assertEqual(tuple(unpack_from('<3I',out,at+0x2C)),(1+i,2+i,3+i))
                self.assertEqual(out[at+0x38],i%2)
                self.assertEqual(out[at+0x41:at+0x47],
                                  bytes([20+i,30+i,40+i,50+i,10+i,10+i]))
                self.assertEqual(out[at+0x47],60+i)
                p=[0,1,5,16,255][i%5]
                self.assertEqual(list(out[at+0x39:at+0x41]),
                                 [min(15,max(0,p-5+(8 if j%2==0 else 12))) for j in range(8)])
            self.assertEqual(out[0x104+(12+side)*0x48:],args['original_side_after_533480_header'][0x104+(12+side)*0x48:])
            self.assertEqual(args['original_side_after_533480_header'],bytes([0xB6])*1556)

    def test_zero_nonzero_status_and_0_15_saturation_are_not_swapped(self):
        args=sample()
        match=bytearray(args['original_match_object'])
        match[0x7c]=0; match[0x81:0x89]=b'\x00\x01\x80\x00\x00\x01\x00\x00'
        got=source_fastview_native_side_roster_stage_533370(**(args|{'original_match_object':bytes(match)}))
        self.assertEqual(list(got[0x104+0x39:0x104+0x41]),[3,7,7,3,3,7,3,3])
        match[0x7c]=255
        got=source_fastview_native_side_roster_stage_533370(**(args|{'original_match_object':bytes(match)}))
        self.assertEqual(list(got[0x104+0x39:0x104+0x41]),[15]*8)

    def test_input_fail_closed_and_does_not_mutate_originals(self):
        args=sample()
        base=source_fastview_native_side_roster_stage_533370(**args)
        for change in (
            {'original_side_index':2}, {'original_side_index':True},
            {'original_match_object':b''}, {'original_match_object':bytearray(args['original_match_object'])},
            {'original_side_after_533480_header':bytes(1555)},
            {'original_ordered_player_rows':list(args['original_ordered_player_rows'])},
            {'original_ordered_player_rows':args['original_ordered_player_rows'][:-1]},
            {'original_533ab0_result':256}, {'original_533ab0_result':None},
            {'original_533ab0_result':True},
        ):
            with self.subTest(change=str(change)[:80]), self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_native_side_roster_stage_533370(**(args|change))
        original_row=args['original_ordered_player_rows'][0]
        for row in (
            SourceFastViewNativePlayerRowInput(original_row.player_record,original_row.player_subobject,b'bad',original_row.byte8_source),
            SourceFastViewNativePlayerRowInput(original_row.player_record,original_row.player_subobject,b'ok\0',b''),
            SourceFastViewNativePlayerRowInput(original_row.player_record,original_row.player_subobject[:2],b'ok\0',b'v'),
            SourceFastViewNativePlayerRowInput(bytearray(original_row.player_record),original_row.player_subobject,b'ok\0',b'v'),
        ):
            with self.subTest(row=row), self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_native_side_roster_stage_533370(**(args|{'original_ordered_player_rows':(row,)+args['original_ordered_player_rows'][1:]}))
        self.assertEqual(source_fastview_native_side_roster_stage_533370(**args),base)

    def test_long_source_name_is_exact_memcpy_without_truncation(self):
        args=sample()
        r=args['original_ordered_player_rows'][0]
        replacement=SourceFastViewNativePlayerRowInput(r.player_record,r.player_subobject,b'A'*50+b'\0',r.byte8_source)
        out=source_fastview_native_side_roster_stage_533370(**(args|{'original_ordered_player_rows':(replacement,)+args['original_ordered_player_rows'][1:]}))
        self.assertEqual(out[0x104:0x104+0x20],b'A'*32)
        # Native subsequent overwrite of row fields, without guessed 32-byte truncation.
        self.assertEqual(out[0x104+0x21:0x104+0x24],b'A'*3)
        self.assertEqual(out[0x104+0x47],60)

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'owner original PE not mounted')
    def test_independent_original_pe_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        samples={
            0x533370:'51 53 8b 5c 24 10',0x53337f:'8b 96 a4 05 00 00',
            0x53338d:'8b 90 54 0b 00 00',0x53339b:'89 90 fc 00 00 00',
            0x5333dd:'e8 1e 06 00 00',0x5333e2:'0f bf 46 10',
            0x5333ec:'e8 df af ee ff',0x5333f3:'88 43 0e',
            0x5333f6:'8a 57 fb',0x5333f9:'83 ea 05',
            0x5333fe:'8a 04 0f',0x533401:'f6 d8',
            0x533403:'1b c0',0x533405:'83 e0 04',
            0x533408:'83 c0 08',0x53340b:'03 c2',
            0x533413:'83 f8 0f',0x53341d:'88 04 0b',
            0x533426:'8b 54 24 18',0x533432:'8b 82 fc 00 00 00',
            0x533462:'e8 19 00 00 00',0x533469:'e8 42 06 00 00',
            0x533476:'89 81 00 01 00 00',
            0x533a00:'8b 44 24 08',0x533a0d:'8d 04 c0',
            0x533a16:'8d ac c1 04 01 00 00',0x533a30:'c1 e9 02',
            0x533a43:'8a 02',0x533a45:'88 45 20',
            0x533a48:'66 8b 4b 04',0x533a4c:'89 4d 24',
            0x533a51:'e8 3a 7a ee ff',0x533a56:'88 45 38',
            0x533a5e:'8b 8b 48 02 00 00',0x533a65:'e8 96 68 fb ff',
            0x533a6a:'89 07',0x533a78:'66 8b 53 6e',
            0x533a7d:'89 55 28',0x533a80:'8a 43 41',
            0x533a83:'88 45 41',0x533a98:'8a 4b 40',
            0x533aa1:'88 55 46',0x41b490:'8b 41 14',
            0x41b493:'c1 e8 0b',0x41b496:'24 01',
            0x41e3d0:'0f bf 41 10',0x41e3da:'8a 41 70',
            0x4ea300:'8b 54 24 04',0x4ea306:'8a 04 0a',
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewClubHeaderDirectFieldTests(unittest.TestCase):
    def test_original_d4_fa_writes_source_copy_repeat_and_byte_wrapping(self):
        from original_fastview_native_player_roster_stage import source_fastview_native_side_header_direct_fields_533480
        club=bytearray((i*17)&0xFF for i in range(0x90))
        club[0x44]=0xFF;club[0x47]=0xFF
        club[0x84]=5
        before=b'\xC7'*1556
        got=source_fastview_native_side_header_direct_fields_533480(
            original_staged_side_1556=before,original_club_record=bytes(club),original_5337c0_result=True)
        self.assertEqual(got[0xD4:0xDC],club[0x84:0x8C])
        self.assertEqual(got[0xDC:0xE0],bytes([0,club[0x4A],club[0x4B],club[0x4C]]))
        self.assertEqual(got[0xE0:0xE4],bytes([0,club[0x56],club[0x57],club[0x58]]))
        self.assertEqual(got[0xE4:0xE8],got[0xDC:0xE0])
        self.assertEqual(got[0xE8:0xEC],got[0xE0:0xE4])
        for target,source in ((0xEC,0x45),(0xED,0x50),(0xEE,0x51),
                              (0xF0,0x48),(0xF1,0x5C),(0xF2,0x5D),
                              (0xF4,0x46),(0xF5,0x53),(0xF6,0x54),
                              (0xF8,0x49),(0xF9,0x5F),(0xFA,0x60)):
            self.assertEqual(got[target],club[source])
        for unchanged in (0,0xD3,0xEF,0xF3,0xF7,0xFB,0xFC,0x103,0x104,1555):
            self.assertEqual(got[unchanged],0xC7)
        self.assertEqual(before,b'\xC7'*1556)

    def test_original_club_no_5337c0_result_zeroes_only_four_words(self):
        from original_fastview_native_player_roster_stage import source_fastview_native_side_header_direct_fields_533480
        club=bytes(range(0x90))
        got=source_fastview_native_side_header_direct_fields_533480(
            original_staged_side_1556=b'\x8A'*1556, original_club_record=club,
            original_5337c0_result=False)
        self.assertEqual(got[0xD4:0xDC],b'\x00'*8)
        self.assertEqual(got[0xDC],0x45)
        for kwargs in ({'original_club_record':club[:0x8B]},
                       {'original_staged_side_1556':b'bad'},
                       {'original_club_record':bytearray(club)},
                       {'original_5337c0_result':1},
                       {'original_5337c0_result':True,'original_club_record':bytes(0x90)}):
            with self.subTest(kwargs=str(kwargs)[:100]),self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_native_side_header_direct_fields_533480(
                    **(dict(original_staged_side_1556=b'\x8A'*1556,
                            original_club_record=club,original_5337c0_result=False)|kwargs))

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'original private PE not mounted')
    def test_original_533480_direct_header_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        samples={
            0x533647:'53',0x533648:'e8 73 01 00 00',
            0x533650:'84 c0',0x533654:'0f bf 8b 84 00 00 00',
            0x533661:'66 89 8d d4 00 00 00',
            0x53366a:'0f bf 8b 86 00 00 00',
            0x533677:'66 89 8d d6 00 00 00',
            0x533680:'0f bf 8b 88 00 00 00',
            0x53368d:'66 89 8d d8 00 00 00',
            0x533696:'0f bf 83 8a 00 00 00',
            0x5336a1:'66 89 85 da 00 00 00',
            0x5336a8:'8a 53 44',0x5336ab:'fe c2',
            0x5336ae:'88 95 dc 00 00 00',
            0x5336cf:'8a 43 47',0x5336d2:'fe c0',
            0x5336f6:'8a 4b 44',0x5336f9:'fe c1',
            0x533742:'8a 43 45',0x533745:'88 85 ec 00 00 00',
            0x53375d:'8a 43 48',0x533760:'88 85 f0 00 00 00',
            0x533778:'8a 43 46',0x53377b:'88 85 f4 00 00 00',
            0x533793:'8a 43 49',0x533796:'88 85 f8 00 00 00',
            0x5337a5:'8a 53 60',0x5337a8:'88 95 fa 00 00 00',
            0x5337c6:'66 83 bf 84 00 00 00 00',
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewFormationRosterMapTests(unittest.TestCase):
    def test_source_5339c0_three_original_formation_groups_first_match_and_counts(self):
        from original_fastview_native_player_roster_stage import source_fastview_native_formation_groups_533480
        args=sample(count=12)
        side=source_fastview_native_side_roster_stage_533370(**args)
        values=((402,400,1000,402),(411,405),(409,407,403))
        actual=source_fastview_native_formation_groups_533480(
            original_staged_side_1556=side,original_4037b0_has_formation=True,
            source_formation_player_id_groups=values)
        self.assertEqual(tuple(unpack_from('<I',actual,o)[0] for o in (0x8C,0xA4,0xBC)),(3,2,3))
        self.assertEqual(tuple(unpack_from('<3I',actual,0x90)),(2,0,2))
        self.assertEqual(tuple(unpack_from('<2I',actual,0xA8)),(11,5))
        self.assertEqual(tuple(unpack_from('<3I',actual,0xC0)),(9,7,3))
        self.assertEqual(actual[0xD4:],side[0xD4:])
        self.assertEqual(side[0x8C:0xD4],b'\xB6'*(0xD4-0x8C))
    def test_source_empty_formation_and_unvisited_source_do_not_overwrite_groups(self):
        from original_fastview_native_player_roster_stage import source_fastview_native_formation_groups_533480
        side=source_fastview_native_side_roster_stage_533370(**sample())
        output=source_fastview_native_formation_groups_533480(
            original_staged_side_1556=side,original_4037b0_has_formation=False,
            source_formation_player_id_groups=None)
        for o in (0x8C,0xA4,0xBC):
            self.assertEqual(unpack_from('<I',output,o)[0],0)
        self.assertEqual(output[0x90:0xA4],side[0x90:0xA4])
        self.assertEqual(output[0xA8:0xBC],side[0xA8:0xBC])
        self.assertEqual(output[0xC0:0xD4],side[0xC0:0xD4])
    def test_group_bad_and_overflow_cases_fail_closed(self):
        from original_fastview_native_player_roster_stage import source_fastview_native_formation_groups_533480
        side=source_fastview_native_side_roster_stage_533370(**sample())
        good=dict(original_staged_side_1556=side,original_4037b0_has_formation=True,
                  source_formation_player_id_groups=((400,),(),()))
        for change in ({'original_staged_side_1556':side[:-1]},
                       {'original_staged_side_1556':bytearray(side)},
                       {'original_4037b0_has_formation':1},
                       {'source_formation_player_id_groups':None},
                       {'source_formation_player_id_groups':((400,),())},
                       {'source_formation_player_id_groups':((400,)*6,(),())},
                       {'source_formation_player_id_groups':((True,),(),())},
                       {'source_formation_player_id_groups':((0x10000,),(),())},
                       {'source_formation_player_id_groups':((400,),[],())},
                       {'original_4037b0_has_formation':False},):
            with self.subTest(change=repr(change)[:80]),self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_native_formation_groups_533480(**(good|change))
    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'private original exe not mounted')
    def test_authentic_original_group_match_instruction_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        samples={
          0x533540:'e8 6b 02 ed ff',0x533547:'0f 84 e6 00 00 00',
          0x53354f:'e8 fc 02 ed ff',0x533564:'8a 86 07 02 00 00',
          0x53357a:'8b 86 64 06 00 00',0x533588:'e8 33 04 00 00',
          0x53359d:'8a 86 09 02 00 00',0x5335a9:'8b 8e 6c 06 00 00',
          0x5335c3:'e8 f8 03 00 00',0x5335d8:'8a 86 08 02 00 00',
          0x5335e4:'8b 96 68 06 00 00',0x5335fe:'e8 bd 03 00 00',
          0x53361f:'89 95 8c 00 00 00',0x533625:'89 85 a4 00 00 00',
          0x53362b:'89 8d bc 00 00 00',0x533633:'33 c0',
          0x5339c0:'8b 4c 24 04',0x5339c7:'8b 91 fc 00 00 00',
          0x5339d5:'81 c1 28 01 00 00',0x5339db:'39 31',
          0x5339e0:'83 c1 48',0x5339e9:'8b 4c 24 14',
          0x5339f3:'89 04 96',0x5339f8:'40',0x5339f9:'89 01',
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewNativeDefaultOptionTests(unittest.TestCase):
    def test_original_533ab0_default_and_registered_modes(self):
        from original_fastview_native_player_roster_stage import source_fastview_original_side_option_533ab0
        base=dict(original_club_word18=0,original_62ac80_virtual30_result=None,
                  original_62ac80_signed_word20=None,original_computed_registry_pointer_nonzero=None,
                  original_registry_slot_bytes=None)
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),11)
        base['original_club_word18']=17
        base['original_62ac80_virtual30_result']=0xA1
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),11)
        base['original_62ac80_virtual30_result']=0
        base['original_62ac80_signed_word20']=-1
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),11)
        base['original_62ac80_signed_word20']=0
        base['original_computed_registry_pointer_nonzero']=False
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),11)
        base['original_computed_registry_pointer_nonzero']=True
        source=bytearray(0x40);source[0x2B]=0
        base['original_registry_slot_bytes']=bytes(source)
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),0)
        source[0x2B]=254
        base['original_registry_slot_bytes']=bytes(source)
        self.assertEqual(source_fastview_original_side_option_533ab0(**base),254)
    def test_original_option_requires_exact_reached_fields_not_guesses(self):
        from original_fastview_native_player_roster_stage import source_fastview_original_side_option_533ab0
        valid=dict(original_club_word18=1,original_62ac80_virtual30_result=0,
                   original_62ac80_signed_word20=5,original_computed_registry_pointer_nonzero=True,
                   original_registry_slot_bytes=bytes(0x40))
        for change in ({'original_club_word18':-1},{'original_club_word18':True},
                       {'original_62ac80_virtual30_result':True},
                       {'original_62ac80_virtual30_result':None},
                       {'original_62ac80_signed_word20':32768},
                       {'original_62ac80_signed_word20':None},
                       {'original_computed_registry_pointer_nonzero':None},
                       {'original_computed_registry_pointer_nonzero':1},
                       {'original_registry_slot_bytes':bytes(0x2B)},
                       {'original_registry_slot_bytes':bytearray(0x40)},
                       {'original_62ac80_signed_word20':-1},
                       {'original_62ac80_virtual30_result':2},
                       {'original_club_word18':0}):
            with self.subTest(change=repr(change)),self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_original_side_option_533ab0(**(valid|change))
    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'private original PE not mounted')
    def test_original_533ab0_branch_and_registry_getter_opcode_proof(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        samples={
          0x533ab0:'8b 44 24 08',0x533abc:'bf 0b 00 00 00',
          0x533ac7:'8b 8e b0 05 00 00',0x533acd:'e8 be 1d ed ff',
          0x533ad2:'66 83 78 18 00',0x533ad9:'8b ce',
          0x533adb:'e8 a0 71 0f 00',0x533ae0:'8b 70 4c',
          0x533ae7:'ff 50 30',0x533aea:'84 c0',
          0x533aee:'66 8b 46 20',0x533af2:'66 85 c0',
          0x533af7:'8b 15 50 6c 87 00',0x533afd:'0f bf c0',
          0x533b00:'c1 e0 06',0x533b03:'03 c2',
          0x533b05:'85 c0',0x533b0c:'8a 48 2b',
          0x533b13:'8b c7',
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewHeaderNativeOwnerTests(unittest.TestCase):
    def test_original_club_human_registry_search_includes_both_match_sides(self):
        from original_fastview_native_player_roster_stage import source_fastview_original_human_club_4037b0
        clubs=(100, 250, 500, 725)
        self.assertEqual(source_fastview_original_human_club_4037b0(original_club_reference_dword=100, original_human_registry_club_ids_in_link_order=clubs),0)
        self.assertEqual(source_fastview_original_human_club_4037b0(original_club_reference_dword=725, original_human_registry_club_ids_in_link_order=clubs),3)
        self.assertIsNone(source_fastview_original_human_club_4037b0(original_club_reference_dword=800, original_human_registry_club_ids_in_link_order=clubs))
        self.assertIsNone(source_fastview_original_human_club_4037b0(original_club_reference_dword=800, original_human_registry_club_ids_in_link_order=()))
        self.assertEqual(source_fastview_original_human_club_4037b0(original_club_reference_dword=100, original_human_registry_club_ids_in_link_order=(100,100)),0)
        for change in ({'original_club_reference_dword':-1}, {'original_club_reference_dword':True},
                       {'original_human_registry_club_ids_in_link_order':(100,)*7},
                       {'original_human_registry_club_ids_in_link_order':(100,True)},
                       {'original_human_registry_club_ids_in_link_order':[100,250]},
                       {'original_human_registry_club_ids_in_link_order':(100,-1)}):
            with self.subTest(change=repr(change)),self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_original_human_club_4037b0(**(dict(original_club_reference_dword=100,original_human_registry_club_ids_in_link_order=clubs)|change))

    def test_original_country_predicate_needs_exact_resolved_global_names(self):
        from original_fastview_native_player_roster_stage import source_fastview_original_country_header_5337c0
        club=bytearray(b'\x00'*0xDA)
        pack_into('<H',club,0x84,1)
        ids=(7,11,14)
        for country,expected in ((7,True),(11,True),(14,True),(22,False)):
            pack_into('<I',club,0x14,country)
            self.assertEqual(source_fastview_original_country_header_5337c0(original_club_record=bytes(club),original_533830_country_indexes_germany_france_england=ids),expected)
        pack_into('<H',club,0x84,0)
        self.assertFalse(source_fastview_original_country_header_5337c0(original_club_record=bytes(club),original_533830_country_indexes_germany_france_england=ids))
        pack_into('<H',club,0x84,1)
        pack_into('<I',club,0x14,0xFFFFFFFF)
        self.assertTrue(source_fastview_original_country_header_5337c0(original_club_record=bytes(club),original_533830_country_indexes_germany_france_england=(-1,11,14)))
        for change in ({'original_club_record':club[:0x85]}, {'original_club_record':club},
                       {'original_533830_country_indexes_germany_france_england':(7,11)},
                       {'original_533830_country_indexes_germany_france_england':(7,11,True)},
                       {'original_533830_country_indexes_germany_france_england':(7,11,-2)},
                       {'original_533830_country_indexes_germany_france_england':(7,11,0x80000000)}):
            with self.subTest(change=repr(change)[:85]),self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_original_country_header_5337c0(**(dict(original_club_record=bytes(club),original_533830_country_indexes_germany_france_england=ids)|change))

    def test_shipped_533980_mode_return_is_source_word_d8_not_arbitrary_game_mode(self):
        from original_fastview_native_player_roster_stage import source_fastview_original_header_mode_word_533980
        data=bytearray(0xDA);pack_into('<H',data,0xD8,0xFEDC)
        self.assertEqual(source_fastview_original_header_mode_word_533980(original_club_record=bytes(data)),0xFEDC)
        for bad in (data,bytes(data[:-1]),None):
            with self.assertRaises(SourceFastViewNativePlayerRosterError):
                source_fastview_original_header_mode_word_533980(original_club_record=bad)

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'private original PE not mounted')
    def test_original_human_and_country_owner_pe_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        samples={
          0x4037b0:'51',0x4037b1:'b9 10 4c 87 00',0x4037b6:'e8 25 02 01 00',
          0x4139e0:'8b 44 24 04',0x4139e4:'8b 40 04',0x4139e8:'e8 03 00 00 00',
          0x4139f0:'8b 81 cc 09 00 00',0x4139fe:'8b 10',
          0x413a00:'8b 92 b4 05 00 00',0x413a06:'39 4a 04',
          0x413a0b:'8b 40 04',0x413a17:'b0 01',
          0x413b40:'8b 81 cc 09 00 00',0x413b4e:'81 e1 ff ff 00 00',
          0x413b56:'8b 92 b4 05 00 00',0x413b5c:'39 4a 04',
          0x403850:'56',0x403853:'e8 58 ff ff ff',
          0x40385c:'8b 46 04',0x403865:'e8 d6 02 01 00',
          0x5337c0:'53',0x5337c6:'66 83 bf 84 00 00 00 00',
          0x5337d1:'68 cc a2 82 00',0x5337db:'68 c4 a2 82 00',
          0x5337e7:'68 bc a2 82 00',0x5337f3:'8b 4f 14',
          0x5337f9:'3b ce',0x533803:'3b c8',
          0x53380c:'e8 8f 5e 12 00',0x533815:'8b 4f 14',
          0x533819:'3b cb',0x53381c:'0f 94 c0',
          0x6596a0:'33 c0 c3',0x533980:'e8 1b 5d 12 00',
          0x533985:'83 e8 00',
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewHumanLow16LookupSeparationTests(unittest.TestCase):
    def test_human_membership_raw_dword_and_formation_owner_word_mask_differ(self):
        from original_fastview_native_player_roster_stage import (
            source_fastview_original_human_club_4037b0,
            source_fastview_original_formation_owner_413b40,
        )
        refs=(0x10001,1,45)
        self.assertEqual(source_fastview_original_human_club_4037b0(original_club_reference_dword=0x10001,original_human_registry_club_ids_in_link_order=refs),0)
        self.assertEqual(source_fastview_original_formation_owner_413b40(original_club_reference_dword=0x10001,original_human_registry_club_ids_in_link_order=refs),1)
        self.assertEqual(source_fastview_original_formation_owner_413b40(original_club_reference_dword=45,original_human_registry_club_ids_in_link_order=refs),2)
        self.assertIsNone(source_fastview_original_formation_owner_413b40(original_club_reference_dword=78,original_human_registry_club_ids_in_link_order=refs))
        self.assertIsNone(source_fastview_original_formation_owner_413b40(original_club_reference_dword=0x10001,original_human_registry_club_ids_in_link_order=(0x10001,)))
        with self.assertRaises(SourceFastViewNativePlayerRosterError):
            source_fastview_original_formation_owner_413b40(original_club_reference_dword=True,original_human_registry_club_ids_in_link_order=refs)

if __name__=='__main__': unittest.main()
