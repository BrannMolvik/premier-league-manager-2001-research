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

if __name__=='__main__': unittest.main()
