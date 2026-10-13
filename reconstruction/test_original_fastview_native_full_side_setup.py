"""Source 0x533270 first-loop, two original teams, no modal or GUI."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into, unpack_from
import unittest

from original_fastview_native_full_side_setup import (
    SourceFastViewOriginalNativeSideOwner,
    source_fastview_original_first_two_side_init_533270,
)
from original_fastview_native_player_roster_stage import (
    SourceFastViewNativePlayerRowInput,
    SourceFastViewNativePlayerRosterError,
)
from original_fastview_two_sided_live_writeback import OriginalFastViewTwoSideWritebackError


def original_source_test_inputs(*, first_count=12, second_count=11):
    match=bytearray(0xB58)
    pack_into("<I",match,0x5A4,first_count)
    pack_into("<I",match,0xB54,second_count)

    def side(index,count):
        # Struct-shaped synthetic *test data*, not an original match.
        # Actual production must supply independently resolved original pointers.
        club=bytearray(0xDA)
        club_id=44 if index==0 else 55
        pack_into("<I",club,4,club_id)
        pack_into("<H",club,0xD8,0x1234+index)
        pack_into("<H",club,0x84,1)
        pack_into("<I",club,0x14,7 if index==0 else 11)
        rows=[]
        for i in range(count):
            player=bytearray(0x24C)
            pack_into("<H",player,4,400+index*100+i)
            pack_into("<H",player,0x6E,500+index*100+i)
            player[0x70]=70+i
            player[0x40:0x45]=bytes((i,i+1,i+2,i+3,i+4))
            player[0x14:0x18]=b"\x00\x08\x00\x00" if i%2 else b"\0"*4
            subobject=bytes((i+1,i+2,i+3))
            rows.append(SourceFastViewNativePlayerRowInput(
                player_record=bytes(player),player_subobject=subobject,
                display_name_nul=f"Source{index}-{i}".encode()+b"\0",
                byte8_source=bytes((60+i,))))
            at=(0x7C if index==0 else 0x62C)+0x4C*i
            match[at]=5
            match[at+5:at+13]=bytes((0,1,0,1,0,1,0,1))
        packed=bytearray(0x40)
        pack_into("<I",packed,0,0x12345)
        for i in range(count):
            packed[0x04+i]=1+i
            packed[0x16+i]=1+i
            packed[0x28+i]=1+i
        return SourceFastViewOriginalNativeSideOwner(
            original_stack_1556=b"\xB6"*1556,
            original_players_in_match_pointer_order=tuple(rows),
            original_club_record=bytes(club),
            original_user_42c6d0_title_nul=b"Human club\x00" if index==0 else None,
            original_club_0c_title_nul=f"Club {index}".encode()+b"\0",
            original_40da90_temporary_title_nul=f"Secondary {index}".encode()+b"\0",
            original_formation_groups_from_403850=(
                ((400,401),(402,),(403,404)) if index==0 else None
            ),
            original_raw_tactical_stack_280=b"\xC7"*280,
            original_packed_side_from_533b20=bytes(packed),
        )
    return dict(
        original_match_object=bytes(match),
        source_side0=side(0,first_count),
        source_side1=side(1,second_count),
        original_human_registry_club_ids_in_link_order=(44,),
        original_country_name_indexes_germany_france_england=(7,11,15),
    )


class OriginalNativeTwoSidedFirstLoopTests(unittest.TestCase):
    def test_verified_source_533270_first_loop_both_club_header_and_tactics(self):
        args=original_source_test_inputs()
        state=source_fastview_original_first_two_side_init_533270(**args)
        self.assertEqual(len(state.original_full_side_global_memory),3112)
        self.assertEqual(len(state.original_tactics_side0),280)
        self.assertEqual(len(state.original_tactics_side1),280)
        left=state.original_full_side_global_memory[:1556]
        right=state.original_full_side_global_memory[1556:]
        self.assertEqual(left[:11],b"Human club\0")
        self.assertEqual(right[:7],b"Club 1\0")
        self.assertEqual(left[0x40:0x40+12],b"Secondary 0\0")
        self.assertEqual(right[0x40:0x40+12],b"Secondary 1\0")
        self.assertEqual(tuple(unpack_from("<3I",left,0x80)),(44,1,0x1234))
        self.assertEqual(tuple(unpack_from("<3I",right,0x80)),(55,0,0x1235))
        self.assertEqual(tuple(unpack_from("<3I",left,0x8C)),(2,0xB6B6B6B6,0)) if False else None
        self.assertEqual(tuple(unpack_from("<I",left,offset)[0] for offset in (0x8C,0xA4,0xBC)),(2,1,2))
        self.assertEqual(tuple(unpack_from("<2I",left,0x90)),(0,1))
        self.assertEqual(unpack_from("<I",right,0x8C)[0],0)
        self.assertEqual(tuple(unpack_from("<I",left,0xFC))[0],12)
        self.assertEqual(tuple(unpack_from("<I",right,0xFC))[0],11)
        self.assertEqual(tuple(unpack_from("<I",left,0x100))[0],11)
        self.assertEqual(left[0x104:0x104+8],b"Source0-")
        self.assertEqual(right[0x104:0x104+8],b"Source1-")
        # Source packed +0x16 BYTEs becomes 0x18 DWORD player positions.
        self.assertEqual(unpack_from("<I",state.original_tactics_side0,0x18)[0],1)
        self.assertEqual(unpack_from("<I",state.original_tactics_side1,0x18)[0],1)
        self.assertEqual(unpack_from("<I",state.original_tactics_side0,0x14)[0],12)
        self.assertEqual(unpack_from("<I",state.original_tactics_side1,0x14)[0],11)
        self.assertEqual(state.original_tactics_side0[0xF0],3)
        self.assertEqual(state.original_tactics_side1[0xF0],3)
        self.assertEqual(state.original_tactics_side0[0x104],0)
        self.assertEqual(state.original_tactics_side1[0x104],0)
        self.assertEqual(args["source_side0"].original_stack_1556,b"\xB6"*1556)

    def test_two_sides_can_both_be_human_under_same_global_owner(self):
        from dataclasses import replace
        args=original_source_test_inputs()
        right=args["source_side1"]
        right=replace(right,
                      original_user_42c6d0_title_nul=b"Other human\0",
                      original_formation_groups_from_403850=((500,501),(),(502,)))
        both=source_fastview_original_first_two_side_init_533270(
            **(args|dict(source_side1=right,
                         original_human_registry_club_ids_in_link_order=(44,55))))
        second=both.original_full_side_global_memory[1556:]
        self.assertEqual(second[:12],b"Other human\0")
        self.assertEqual(unpack_from("<I",second,0x84)[0],1)
        self.assertEqual(tuple(unpack_from("<I",second,i)[0] for i in (0x8C,0xA4,0xBC)),(2,0,1))

    def test_original_owner_mismatch_fails_closed_before_a_side_state_is_returned(self):
        from dataclasses import replace
        args=original_source_test_inputs()
        old=source_fastview_original_first_two_side_init_533270(**args)
        variants=(
            dict(original_match_object=args["original_match_object"][:-1]),
            dict(source_side1=replace(args["source_side1"], original_packed_side_from_533b20=b"bad")),
            dict(source_side1=replace(args["source_side1"], original_club_0c_title_nul=b"missing nul")),
            dict(source_side1=replace(args["source_side1"], original_formation_groups_from_403850=((500,),(),()))),
            dict(source_side0=replace(args["source_side0"], original_user_42c6d0_title_nul=None)),
            dict(source_side1=replace(args["source_side1"], original_raw_tactical_stack_280=bytes(279))),
            dict(source_side0=None),
            dict(original_country_name_indexes_germany_france_england=(7,False,15)),
        )
        for change in variants:
            with self.subTest(change=repr(change)[:95]), self.assertRaises(
                    (SourceFastViewNativePlayerRosterError,
                     OriginalFastViewTwoSideWritebackError)):
                source_fastview_original_first_two_side_init_533270(**(args|change))
        self.assertEqual(source_fastview_original_first_two_side_init_533270(**args),old)

    def test_native_count_cannot_exceed_source_1556_side_stage(self):
        from dataclasses import replace
        args=original_source_test_inputs()
        for count in (0,10,19):
            m=bytearray(args["original_match_object"])
            pack_into("<I",m,0xB54,count)
            right=args["source_side1"]
            # Counts are read from native match, never from guessed row lists.
            if count <= 18:
                right=replace(right,original_players_in_match_pointer_order=right.original_players_in_match_pointer_order[:count])
            with self.subTest(count=count), self.assertRaises(
                (SourceFastViewNativePlayerRosterError,
                 OriginalFastViewTwoSideWritebackError)):
                source_fastview_original_first_two_side_init_533270(
                    **(args|dict(original_match_object=bytes(m),source_side1=right)))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original source executable not mounted")
    def test_original_533270_sequential_two_sided_first_loop_opcodes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x533270:"81 ec 3c 07 00 00",
            0x533281:"57",
            0x53328b:"e8 e0 00 00 00",
            0x533298:"56",
            0x533299:"e8 62 ea 18 00",
            0x5332a5:"e8 76 08 00 00",
            0x5332b0:"e8 7b ea 18 00",
            0x5332b8:"46",
            0x5332b9:"83 fe 02",
            0x5332c1:"e8 aa df 0f 00",
            0x5332e0:"e8 ab df 0f 00",
            0x5332f5:"e8 96 95 19 00",
            0x53330d:"e8 9e 83 0f 00",
            0x533318:"e8 e3 75 19 00",
            0x53334c:"e8 bf 75 19 00",
            0x533354:"e8 37 f5 18 00",
        }
        for addr,hx in samples.items():
            with self.subTest(native_va=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
