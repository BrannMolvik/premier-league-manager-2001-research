"""Seven original LeagueMatch process callback vtables and bounded +0x34 wrapper."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack, pack_into
import unittest

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    source_original_leaguematch_process_owners_for_native_record,
    source_original_wrapped_prepare_511120_post_base,
    source_original_leaguematch_native_virtual30_low_byte,
    source_original_match_owned_event_collection_4f3b50,
)


def native_match(vtable, *, special_owner=0x12345000, dword50=0xAABBCCDD):
    r=bytearray(0x58)
    pack_into("<I",r,0,vtable)
    pack_into("<I",r,0x50,dword50)
    pack_into("<I",r,0x54,special_owner)
    return bytes(r)


class LeagueMatchNativeProcessingOwnersTests(unittest.TestCase):
    def test_all_seven_original_vtables_have_distinct_source_callback_owners(self):
        self.assertEqual(len(SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS),7)
        wrapped=[]
        for vt, expected in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                got=source_original_leaguematch_process_owners_for_native_record(
                    original_match_record=native_match(vt))
                self.assertEqual((
                    got.virtual28_kind_va,got.virtual30_owner_va,
                    got.virtual34_prepare_va,got.virtual38_cleanup_va,
                    got.virtual3c_cleanup_va,got.virtual44_owner_va), expected)
                self.assertEqual(got.source_wrapped_prepare,expected[2]==0x511120)
                if got.source_wrapped_prepare: wrapped.append(vt)
        self.assertEqual(set(wrapped),{0x7C9D9C,0x7C9E80,0x7C9EF8,0x7C9F70})

    def test_source_wrapper_writes_special_owner_before_conditioned_d24(self):
        original=native_match(0x7C9F70,dword50=0x1234ACDC)
        true=source_original_wrapped_prepare_511120_post_base(
            original_match_record=original,
            original_base_510d60_al_nonzero=True,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=0xDEADBEEF,
            original_reached_513e70_result=0xFFFFFFFF,
        )
        self.assertEqual(true.original_written_context_dwords,
                         ((0xD28,0xDEADBEEF),(0xD2C,0xFFFFFFFF),
                          (0xD24,0x1234ACDC)))
        self.assertTrue(true.returned_al_nonzero)
        false=source_original_wrapped_prepare_511120_post_base(
            original_match_record=original,
            original_base_510d60_al_nonzero=False,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=0,
            original_reached_513e70_result=1)
        self.assertEqual(false.original_written_context_dwords,
                         ((0xD28,0),(0xD2C,1)))
        self.assertFalse(false.returned_al_nonzero)

    def test_non5_kind_skips_special_owner_even_with_nonzero_source_pointer(self):
        for kind in (0,1,2,3,4,6,0xFFFFFFFF):
            for base_result in (False,True):
                got=source_original_wrapped_prepare_511120_post_base(
                    original_match_record=native_match(0x7C9D9C,dword50=0),
                    original_base_510d60_al_nonzero=base_result,
                    original_native_kind_from_virtual28=kind)
                self.assertEqual(got.original_written_context_dwords,
                                 ((0xD24,0),) if base_result else ())
                self.assertEqual(got.returned_al_nonzero,base_result)

    def test_native_virtual30_distinguishes_unconditional_zero_and_source_kind2(self):
        primary={0x7C4C24,0x7C4CE4,0x7C9E14}
        special=set(SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS)-primary
        for vt in primary:
            with self.subTest(vtable=hex(vt)):
                record=native_match(vt)
                self.assertEqual(source_original_leaguematch_native_virtual30_low_byte(
                    original_match_record=record),0)
                self.assertEqual(source_original_match_owned_event_collection_4f3b50(
                    original_match_record=record),0x947AD8)
                with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                    source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=record,original_reached_virtual28_kind=2)
        for vt in special:
            for kind,flag,al in ((2,0,1),(2,4,0),(2,0x100,1),(3,0,0),(0,0,0)):
                with self.subTest(vtable=hex(vt),kind=kind,flag=flag):
                    record=bytearray(native_match(vt))
                    pack_into("<I",record,0x44,flag)
                    got=source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=bytes(record),
                        original_reached_virtual28_kind=kind)
                    self.assertEqual(got,al)
                    self.assertEqual(source_original_match_owned_event_collection_4f3b50(
                        original_match_record=bytes(record),
                        original_reached_virtual28_kind=kind),
                        0x947AF0 if al else 0x947AD8)
            for kind in (None,True,-1,0x100000000,"2"):
                with self.subTest(vtable=hex(vt),kind=kind),self.assertRaises(
                    OriginalLeagueMatchProcessOwnerError):
                    source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=native_match(vt),
                        original_reached_virtual28_kind=kind)
            with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                source_original_leaguematch_native_virtual30_low_byte(
                    original_match_record=native_match(vt)[:0x44],
                    original_reached_virtual28_kind=2)

    def test_original_native_unknown_inputs_are_not_inferred_or_defaulted(self):
        for record in (b"",bytes(3),bytearray(native_match(0x7C9D9C)),
                       native_match(0xDEADBEEF)):
            with self.subTest(record=str(record)[:30]),self.assertRaises(
                OriginalLeagueMatchProcessOwnerError):
                source_original_leaguematch_process_owners_for_native_record(
                    original_match_record=record)
        good=dict(
            original_match_record=native_match(0x7C9D9C),
            original_base_510d60_al_nonzero=True,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=1,
            original_reached_513e70_result=2)
        for changes in (
            {"original_match_record":native_match(0x7C4C24)},
            {"original_match_record":native_match(0x7C9D9C,special_owner=0)},
            {"original_match_record":bytes(0x57)},
            {"original_native_kind_from_virtual28":None},
            {"original_native_kind_from_virtual28":True},
            {"original_native_kind_from_virtual28":-1},
            {"original_native_kind_from_virtual28":0x100000000},
            {"original_base_510d60_al_nonzero":1},
            {"original_reached_513e80_result":None},
            {"original_reached_513e70_result":True},
            {"original_reached_513e70_result":-1},
            {"original_native_kind_from_virtual28":4},
        ):
            with self.subTest(changes=str(changes)[:80]),self.assertRaises(
                OriginalLeagueMatchProcessOwnerError):
                source_original_wrapped_prepare_511120_post_base(**(good|changes))

    def test_original_510d60_two_event_counters_all_six_literal_kinds(self):
        from original_leaguematch_native_process_owners import (
            source_original_510d60_two_event_counter_writes,
        )
        # Native six vtable+28 methods are literal return functions:
        # these expected native results are from the original PE.
        kinds={
            0x7C4C24:1,0x7C9D9C:2,0x7C9E14:6,
            0x7C9E80:3,0x7C9EF8:4,0x7C9F70:5,
        }
        for vt,kind in kinds.items():
            for flags in (0,1,2,3,4,5,6,7,0xFFFFFFFF):
                with self.subTest(vtable=hex(vt),flags=flags):
                    source=bytearray(native_match(vt))
                    pack_into("<I",source,0x44,flags)
                    result=source_original_510d60_two_event_counter_writes(
                        original_match_record=bytes(source))
                    d0c=0 if kind==2 and flags & 4==0 else ((flags>>1)&1)
                    d10=1 if kind==3 and flags & 4==0 else ((flags>>2)&1)
                    self.assertEqual(result.source_context_stores,
                                     ((0xD0C,d0c),(0xD10,d10),
                                      (0xD14,int(kind==5)),
                                      (0xD18,(flags>>3)&1),
                                      (0xD24,0xFFFFFFFF),
                                      (0xD28,0xFFFFFFFF),
                                      (0xD2C,0xFFFFFFFF)))
                    self.assertEqual(result.original_virtual28_literal_kind,kind)
                    self.assertFalse(result.original_base_510d60_executed)
                    self.assertFalse(result.live_game_state_updated)

    def test_original_510d60_counters_reject_diagnostic_kind_and_unreached_flags(self):
        from original_leaguematch_native_process_owners import (
            source_original_510d60_two_event_counter_writes,
        )
        bad=(native_match(0x7C4CE4),
             native_match(0x7C4C24)[:0x47],
             native_match(0x7C4C24)[:0x40],
             native_match(0x7C4C24).replace(pack("<I",0x7C4C24),pack("<I",0xDEADBEEF),1))
        for record in bad:
            with self.subTest(length=len(record),head=record[:4]):
                with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                    source_original_510d60_two_event_counter_writes(
                        original_match_record=record)
        with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
            source_original_510d60_two_event_counter_writes(
                original_match_record=bytearray(native_match(0x7C4C24)))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "private original executable not mounted in hosted CI")
    def test_all_native_virtual_slots_and_wrapper_opcodes_match_original(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt, members in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                self.assertEqual(pe.read(vt+0x10,4),pack("<I",0x513010))
                self.assertEqual(pe.read(vt+0x18,4),pack("<I",0x6559A0))
                for off,value in zip((0x28,0x30,0x34,0x38,0x3C,0x44),members):
                    self.assertEqual(pe.read(vt+off,4),pack("<I",value))
        sites={
            0x651980:"32 c0 c3",
            0x5112C0:"56",0x5112C5:"ff 50 28",
            0x5112C8:"83 f8 02",0x5112CD:"f6 46 44 04",
            0x5112D3:"b0 01",0x5112D7:"32 c0",
            0x5130B7:"c7 84 24 6c 11 00 00 00 00 00 00",
            0x5130C2:"ff 50 34",0x5130C5:"84 c0",
            0x5130C9:"8d 54 24 08",
            0x511120:"53 56 57",0x51112A:"e8 31 fc ff ff",
            0x51112F:"8a d8",0x511135:"ff 50 28",
            0x511138:"83 f8 05",0x51113D:"8b 4e 54",
            0x511140:"e8 3b 2d 00 00",0x511145:"89 87 28 0d 00 00",
            0x51114B:"8b 4e 54",0x51114E:"e8 1d 2d 00 00",
            0x511153:"89 87 2c 0d 00 00",0x511159:"84 db",
            0x51115D:"8b 4e 50",0x511160:"89 8f 24 0d 00 00",
            0x511167:"8a c3",0x51116B:"c2 04 00",
            0x510D60:"51",0x510D73:"e8 d8 17 12 00",
            0x510D95:"8b 0d 30 75 87 00",
            0x510D9B:"89 8e 3c 0d 00 00",
            # Original 510D60 virtual+28 constants and counter writes.
            0x651E20:"b8 01 00 00 00 c3",
            0x6CE1E0:"b8 02 00 00 00 c3",
            0x650250:"b8 06 00 00 00 c3",
            0x6CE1F0:"b8 03 00 00 00 c3",
            0x6CECB0:"b8 04 00 00 00 c3",
            0x650010:"b8 05 00 00 00 c3",
            0x668766:"6a 19",0x668768:"e8 62 24 00 00",
            0x510DBF:"ff 52 28",0x510DC2:"83 f8 02",
            0x510DC7:"f6 45 44 04",
            0x510DCF:"89 be 0c 0d 00 00",
            0x510DD7:"8b 45 44",0x510DDA:"d1 e8",
            0x510DDC:"83 e0 01",0x510DE1:"89 86 0c 0d 00 00",
            0x510DEC:"ff 52 28",0x510DEF:"83 f8 03",
            0x510DF4:"f6 45 44 04",
            0x510DFA:"c7 86 10 0d 00 00 01 00 00 00",
            0x510E06:"8b 45 44",0x510E09:"c1 e8 02",
            0x510E0C:"83 e0 01",0x510E0F:"89 86 10 0d 00 00",
            0x510E1A:"ff 52 28",0x510E1F:"83 f8 05",
            0x510E22:"0f 94 c1",0x510E25:"89 8e 14 0d 00 00",
            0x510E2B:"8b 55 44",0x510E2E:"c1 ea 03",
            0x510E31:"83 e2 01",0x510E34:"89 96 18 0d 00 00",
            0x510E55:"83 c8 ff",0x510E58:"89 86 24 0d 00 00",
            0x510E5E:"89 86 28 0d 00 00",
            0x510E64:"89 86 2c 0d 00 00",
        }
        for addr,hx in sites.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))



class LeagueMatchV34SourceReadinessReturnTests(unittest.TestCase):
    """Original 510D60 zero/one 407770 gate sequence, not a live match."""

    def project(self, vtable=0x7C4C24, gates=(True,True,True,True),
                special=(None,None)):
        from original_leaguematch_native_process_owners import (
            source_original_510d60_four_readiness_gate_return as project)
        return project(
            original_match_record=native_match(vtable),
            original_first_team_407770_zero_nonzero=gates[0],
            original_second_team_407770_zero_nonzero_if_reached=gates[1],
            original_first_team_407770_one_nonzero_if_reached=gates[2],
            original_second_team_407770_one_nonzero_if_reached=gates[3],
            original_reached_513e80_result_if_wrapped_kind5=special[0],
            original_reached_513e70_result_if_wrapped_kind5=special[1])

    def test_four_source_407770_zero_then_one_short_circuit_exit_sites(self):
        scenarios=[
            ((False,None,None,None),False,0x511115,1),
            ((True,False,None,None),False,0x511115,2),
            ((True,True,False,None),False,0x5110FF,3),
            ((True,True,True,False),False,0x5110FF,4),
            ((True,True,True,True),True,0x5110E7,4),
        ]
        for gates,al,site,count in scenarios:
            with self.subTest(gates=gates):
                r=self.project(gates=gates)
                self.assertEqual(r.original_base_510d60_al_nonzero,al)
                self.assertEqual(r.original_base_exit_va,site)
                self.assertEqual(r.reached_gate_addresses,
                    (0x510EE5,0x510EF9,0x510FFA,0x51100F)[:count])
                self.assertEqual(r.reached_gate_nonzero,gates[:count])
                self.assertEqual(r.source_zeroed_context_dword_offsets,
                    () if al else (0x5A4,0xB54))
                self.assertIsNone(r.original_511120_wrapper_post_base)
                self.assertFalse(r.original_complete_v34_context_mutations_proven)
                self.assertFalse(r.live_game_state_modified)

    def test_all_six_original_literal_class_kinds_and_wrapped_kind5(self):
        for vtable in (0x7C4C24,0x7C9D9C,0x7C9E14,0x7C9E80,0x7C9EF8,0x7C9F70):
            wrapped=vtable in (0x7C9D9C,0x7C9E80,0x7C9EF8,0x7C9F70)
            special=(0x123,0x456) if vtable==0x7C9F70 else (None,None)
            for al,gates in ((True,(True,True,True,True)),
                             (False,(True,True,True,False))):
                with self.subTest(vtable=hex(vtable),al=al):
                    result=self.project(vtable,gates,special)
                    wrap=result.original_511120_wrapper_post_base
                    self.assertEqual(wrap is not None,wrapped)
                    if wrap:
                        self.assertEqual(wrap.returned_al_nonzero,al)
                        if vtable==0x7C9F70:
                            self.assertEqual(wrap.original_written_context_dwords,
                                ((0xD28,0x123),(0xD2C,0x456))+
                                (((0xD24,0xAABBCCDD),) if al else ()))
                        else:
                            self.assertEqual(wrap.original_written_context_dwords,
                                ((0xD24,0xAABBCCDD),) if al else ())

    def test_reject_unvisited_callbacks_and_unsupported_vtable(self):
        for gate in (
            (True,None,None,None),
            (True,True,None,None),
            (True,True,True,None),
            (False,False,None,None),
            (False,None,None,True),
            (True,False,False,None),
            (True,True,False,True),
            (True,True,True,1),
            (1,None,None,None),
        ):
            with self.subTest(gate=gate),self.assertRaises(
                    OriginalLeagueMatchProcessOwnerError):
                self.project(gates=gate)
        for vt,extra in ((0x7C4CE4,(None,None)),
                         (0x12345678,(None,None)),
                         (0x7C4C24,(0,1)),
                         (0x7C9F70,(None,None)),
                         (0x7C9D9C,(0,1))):
            with self.subTest(vt=hex(vt),extra=extra),self.assertRaises(
                    OriginalLeagueMatchProcessOwnerError):
                self.project(vt,special=extra)

    def test_private_original_pe_gate_and_epilogue_opcode_signatures(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:
            self.skipTest("Private original executable is optional in CI")
        from hashlib import sha256
        pe=Path(original).read_bytes()
        self.assertEqual((len(pe),sha256(pe).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x510EE5:"e8 86 68 ef ff",
            0x510EEC:"0f 84 14 02 00 00",
            0x510EF9:"e8 72 68 ef ff",
            0x510F00:"0f 84 00 02 00 00",
            0x510FFA:"e8 71 67 ef ff",
            0x511001:"0f 84 e7 00 00 00",
            0x51100F:"e8 5c 67 ef ff",
            0x511016:"0f 84 d2 00 00 00",
            0x5110E7:"b0 01",
            0x5110F1:"89 86 a4 05 00 00",
            0x5110FD:"5e 5d 32 c0",
            0x511106:"89 be a4 05 00 00",
            0x51110C:"89 be 54 0b 00 00",
            0x511115:"32 c0",
            0x51112A:"e8 31 fc ff ff",
            0x511145:"89 87 28 0d 00 00",
            0x511153:"89 87 2c 0d 00 00",
            0x511159:"84 db 74 09",
            0x511166:"5f 8a c3",
        }
        for va,sig in sites.items():
            with self.subTest(va=hex(va)):
                value=bytes.fromhex(sig)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(value)],value)




class Original407770NativeRosterSourceTests(unittest.TestCase):
    def source_team(self, count=11, player_ids=None, kind_byte74=0):
        r=bytearray(0x298)
        pack_into("<i",r,0x294,count)
        r[0x74]=kind_byte74
        if player_ids is None:player_ids=tuple(range(101,101+max(count,0)))
        for index,pid in enumerate(player_ids):
            if 0x244+2*index+2 <= len(r):
                pack_into("<H",r,0x244+2*index,pid)
        return bytes(r)

    def project(self, *, count=11, argument=0, ids=None, kind_byte74=0, **kwargs):
        from original_native_407770_roster_eligibility import (
            source_original_407770_reached_roster_gate)
        return source_original_407770_reached_roster_gate(
            original_team_record=self.source_team(count,ids,kind_byte74),
            original_407770_argument=argument,**kwargs)

    def test_roster_under_11_original_always_fails_early_without_day_callbacks(self):
        for count in (-1,0,1,10):
            for arg in (0,1):
                with self.subTest(count=count,arg=arg):
                    x=self.project(count=count,argument=arg)
                    self.assertFalse(x.original_return_eax_nonzero)
                    self.assertEqual(x.reached_4ea300_player_ids,())
                    self.assertFalse(x.native_407770_executed)

    def test_native_arg0_exact_player_day_boundaries_and_short_circuit(self):
        from original_native_407770_roster_eligibility import SourceOriginal407770PlayerDayResult as Row
        ids=tuple(range(101,112))
        good=tuple(Row(pid,5) for pid in ids)
        base=dict(original_current_day_874b64_if_arg0=6)
        success=self.project(argument=0,ids=ids,
            original_reached_4ea300_player_results_if_arg0=good,**base)
        self.assertTrue(success.original_return_eax_nonzero)
        self.assertEqual(success.reached_4ea300_player_ids,ids)
        for value in (0,255,6,7):
            with self.subTest(value=value):
                early=good[:3]+(Row(ids[3],value),)
                result=self.project(argument=0,ids=ids,
                    original_reached_4ea300_player_results_if_arg0=early,**base)
                self.assertFalse(result.original_return_eax_nonzero)
                self.assertEqual(result.reached_4ea300_player_ids,ids[:4])

    def test_native_arg1_403640_bang_name_and_407220_routes(self):
        shared=dict(original_reached_406be0_eax_if_arg1=1)
        yes=self.project(argument=1,kind_byte74=2,original_reached_403640_al_if_arg1=True,**shared)
        self.assertTrue(yes.original_return_eax_nonzero)
        yes=self.project(argument=1,original_reached_403640_al_if_arg1=False,
                         original_team_name_first_byte_if_reached=0x21,**shared)
        self.assertTrue(yes.original_return_eax_nonzero)
        no=self.project(argument=1,original_reached_403640_al_if_arg1=False,
                        original_team_name_first_byte_if_reached=0x41,
                        original_reached_407220_edi_if_arg1=10,**shared)
        self.assertFalse(no.original_return_eax_nonzero)
        yes=self.project(argument=1,original_reached_403640_al_if_arg1=False,
                         original_team_name_first_byte_if_reached=0x41,
                         original_reached_407220_edi_if_arg1=11,**shared)
        self.assertTrue(yes.original_return_eax_nonzero)
        self.assertFalse(self.project(argument=1,kind_byte74=3,
                         original_reached_403640_al_if_arg1=True,
                         original_reached_406be0_eax_if_arg1=2).original_return_eax_nonzero)

    def test_407770_rejects_synthetic_and_unreached_leaves(self):
        from original_native_407770_roster_eligibility import (
            Original407770SourceError,SourceOriginal407770PlayerDayResult as Row)
        cases=[
            dict(count=10,argument=0,original_current_day_874b64_if_arg0=3),
            dict(argument=2),
            dict(argument=True),
            dict(argument=0,original_current_day_874b64_if_arg0=9),
            dict(argument=0,original_current_day_874b64_if_arg0=9,
                 original_reached_4ea300_player_results_if_arg0=(Row(999,1),)),
            dict(argument=0,original_current_day_874b64_if_arg0=9,
                 original_reached_4ea300_player_results_if_arg0=(Row(101,0),Row(102,2))),
            dict(argument=0,original_current_day_874b64_if_arg0=9,
                 original_reached_4ea300_player_results_if_arg0=(Row(101,2),)),
            dict(argument=0,original_current_day_874b64_if_arg0=9,
                 original_reached_4ea300_player_results_if_arg0=()),
            dict(argument=1,original_reached_403640_al_if_arg1=True),
            dict(argument=1,original_reached_403640_al_if_arg1=True,
                 original_team_name_first_byte_if_reached=0x21,
                 original_reached_406be0_eax_if_arg1=1),
            dict(argument=1,original_reached_403640_al_if_arg1=False,
                 original_team_name_first_byte_if_reached=0x21,
                 original_reached_407220_edi_if_arg1=11,
                 original_reached_406be0_eax_if_arg1=1),
            dict(argument=1,original_reached_403640_al_if_arg1=False,
                 original_team_name_first_byte_if_reached=0x41,
                 original_reached_406be0_eax_if_arg1=1),
            dict(argument=1,original_reached_403640_al_if_arg1=True,
                 original_reached_406be0_eax_if_arg1=True),
            dict(argument=1,original_reached_403640_al_if_arg1=False,
                 kind_byte74=2,original_reached_406be0_eax_if_arg1=1),
            dict(argument=0,original_current_day_874b64_if_arg0=9,
                 original_reached_4ea300_player_results_if_arg0=(Row(101,-1),)),
        ]
        for case in cases:
            with self.subTest(case=str(case)[:110]),self.assertRaises(Original407770SourceError):
                self.project(**case)

    def test_optional_canonical_pe_407770_original_branch_signatures(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("private original PE not available")
        from hashlib import sha256
        raw=Path(original).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x40777B:"8b 86 94 02 00 00",
            0x407781:"83 f8 0b",
            0x407784:"0f 8c bc 00 00 00",
            0x407791:"85 c9",
            0x407793:"74 58",
            0x407797:"e8 a4 be ff ff",
            0x4077A5:"80 39 21",
            0x4077B6:"e8 65 fa ff ff",
            0x4077CA:"e8 11 f4 ff ff",
            0x4077CF:"83 ff 0b",
            0x4077D8:"83 f8 01",
            0x4077F3:"8d be 44 02 00 00",
            0x407801:"66 8b 07",
            0x407816:"e8 e5 2a 0e 00",
            0x40781B:"3b 05 64 4b 87 00",
            0x407821:"7d 6e",
            0x407823:"85 c0",
            0x407825:"7e 6a",
            0x407827:"8b 86 94 02 00 00",
            0x40782D:"43",
            0x407831:"3b d8",
            0x407835:"5f 5e",
            0x407837:"b8 01 00 00 00",
            0x407846:"8b 56 0c",
            0x407889:"e8 e1 0e 26 00",
            0x407891:"5f 5e 33 c0",
            0x4EA300:"8b 54 24 04",
            0x4EA304:"33 c0",
            0x4EA306:"8a 04 0a",
            0x4EA309:"c2 04 00",
            0x403640:"8a 41 74",
            0x403643:"3c 02",
            0x403647:"3c 03",
            0x40364B:"33 c0",
            0x40364E:"b8 01 00 00 00",
        }
        for address,expected in sites.items():
            with self.subTest(address=hex(address)):
                b=bytes.fromhex(expected)
                self.assertEqual(raw[address-0x400000:address-0x400000+len(b)],b)




class SourceOriginal406BE0RosterCountTests(unittest.TestCase):
    """Original 406BE0(1,0), 417EE0 and 4EA3C0 exact recorded fields."""

    @staticmethod
    def team(ids=(51,52,53),key=7):
        x=bytearray(0x298)
        pack_into("<I",x,4,key)
        pack_into("<i",x,0x294,len(ids))
        for index,pid in enumerate(ids):
            pack_into("<H",x,0x244+2*index,pid)
        return bytes(x)

    @staticmethod
    def player(pid,club=7,active=True,status=1,base=0x40000000):
        from original_native_406be0_roster_count import SourceOriginal406BE0Player
        raw=bytearray(0x24c)
        pack_into("<h",raw,0x10,club)
        pack_into("<I",raw,0x14,0x10 if active else 0)
        if status is None:
            pack_into("<I",raw,0x248,0)
        else:
            pack_into("<I",raw,0x248,0x51000000+pid*8)
        flags=None if status is None else bytes((0,0,0,status))
        return SourceOriginal406BE0Player(pid,base+pid*0x250,bytes(raw),flags)

    @staticmethod
    def project(team,players):
        from original_native_406be0_roster_count import (
            source_original_406be0_arg1_one_arg2_zero_roster_count)
        return source_original_406be0_arg1_one_arg2_zero_roster_count(
            original_team_record=team,
            original_global_875640_player_array_address=0x40000000,
            original_ordered_player_records=players)

    def test_4ea3c0_masks_player_status_low_five_bits_for_role_one(self):
        ids=(51,52,53)
        ps=(self.player(51,status=0x21),
            self.player(52,status=2),
            self.player(53,status=0x41))
        result=self.project(self.team(ids),ps)
        self.assertEqual(result.source_return_eax,2)
        self.assertEqual(result.reached_417ee0_player_ids,ids)
        self.assertEqual(result.reached_4ea3c0_player_ids,ids)
        self.assertEqual(result.matched_4ea3c0_role_one_player_ids,(51,53))
        self.assertFalse(result.native_406be0_executed)
        self.assertFalse(result.live_game_state_modified)

    def test_417ee0_signed_team_full_key_and_flag_bit4_skip_status(self):
        ids=(51,52,53)
        ps=(self.player(51,club=7,active=True,status=1),
            self.player(52,club=8,active=True,status=None),
            self.player(53,club=7,active=False,status=None))
        result=self.project(self.team(ids),ps)
        self.assertEqual(result.source_return_eax,1)
        self.assertEqual(result.reached_4ea3c0_player_ids,(51,))
        self.assertEqual(result.matched_4ea3c0_role_one_player_ids,(51,))
        # Original MOVSX WORD can match full UINT32 0xffffffff.
        x=self.project(self.team((51,),key=0xffffffff),
                       (self.player(51,club=-1,status=1),))
        self.assertEqual(x.source_return_eax,1)
        # Two role-one players do NOT satisfy outer 407770 EAX==1.
        self.assertNotEqual(self.project(self.team((51,52)),
            (self.player(51,status=1),self.player(52,status=1))).source_return_eax,1)

    def test_negative_or_zero_roster_short_circuits(self):
        for count in (-3,0):
            t=bytearray(self.team(()))
            pack_into("<i",t,0x294,count)
            x=self.project(bytes(t),())
            self.assertEqual(x.source_return_eax,0)
            self.assertEqual(x.reached_417ee0_player_ids,())

    def test_actual_407770_arg1_composes_original_role_one_count_not_truthy_count(self):
        from original_native_406be0_roster_count import (
            source_original_407770_arg1_with_406be0_original_player_bytes as compose)
        for role1_count,expected in ((0,False),(1,True),(2,False)):
            ps=tuple(self.player(pid,status=1 if i<role1_count else 2)
                     for i,pid in enumerate(range(51,62)))
            result=compose(original_team_record=self.team(tuple(range(51,62))),
                           original_global_875640_player_array_address=0x40000000,
                           original_ordered_player_records=ps,
                           original_reached_403640_al=False,
                           original_team_name_first_byte_if_reached=0x41,
                           original_reached_407220_edi_if_reached=11)
            self.assertEqual(result.original_406be0_count.source_return_eax,role1_count)
            self.assertEqual(result.original_407770_arg1_receipt.original_return_eax_nonzero,expected)
            self.assertFalse(result.live_native_match_executed)
            self.assertFalse(result.live_game_state_modified)
        from original_native_406be0_roster_count import Original406BE0SourceError
        with self.assertRaises(Original406BE0SourceError):
            compose(original_team_record=self.team((51,)),
                original_global_875640_player_array_address=0x40000000,
                original_ordered_player_records=(self.player(51),),
                original_reached_403640_al=False,
                original_team_name_first_byte_if_reached=0x41,
                original_reached_407220_edi_if_reached=11)

    def test_original_pointer_and_reached_input_fail_closed(self):
        from original_native_406be0_roster_count import (
            SourceOriginal406BE0Player,Original406BE0SourceError)
        valid=self.player(51)
        t=self.team((51,))
        cases=(
            (t,()),(t,(self.player(52),)),
            (t,(SourceOriginal406BE0Player(51,0x1,valid.original_player_record_bytes,
                                           valid.original_4ea3c0_status_record_if_417ee0_true),)),
            (t,(SourceOriginal406BE0Player(51,valid.original_player_record_native_pointer,
                                           bytes(2),bytes(4)),)),
            (t,(SourceOriginal406BE0Player(51,valid.original_player_record_native_pointer,
                                           valid.original_player_record_bytes,None),)),
            (t,(self.player(51,active=False,status=1),)),
            (t,(self.player(51,club=8,status=1),)),
            (self.team((51,52)),(valid,)),
        )
        for team,players in cases:
            with self.subTest(players=str(players)[:70]),self.assertRaises(Original406BE0SourceError):
                self.project(team,players)

    def test_canonical_original_static_406be0_417ee0_4ea3c0_signatures(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("private original EXE optional in CI")
        from hashlib import sha256
        pe=Path(original).read_bytes()
        self.assertEqual((len(pe),sha256(pe).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x406BE5:"33 c0",
            0x406BED:"8b 8f 94 02 00 00",
            0x406BFD:"8d b7 44 02 00 00",
            0x406C05:"66 8b 06",
            0x406C19:"3b cd",
            0x406C21:"e8 ba 12 01 00",
            0x406C26:"85 c0",
            0x406C2C:"66 8b 06",
            0x406C35:"a1 40 56 87 00",
            0x406C3D:"8b 8c 02 48 02 00 00",
            0x406C44:"e8 77 37 0e 00",
            0x406C49:"3b 44 24 18",
            0x406C4F:"ff 44 24 10",
            0x417EE0:"0f bf 41 10",
            0x417EE4:"39 44 24 04",
            0x417EEF:"8b 41 14",
            0x417EF2:"c1 e8 04",
            0x417EF5:"83 e0 01",
            0x4EA3C0:"8a 41 03",
            0x4EA3C3:"83 e0 1f",
            0x4EA3C6:"c3",
        }
        for va,bytes_hex in sites.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(bytes_hex)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(bs)],bs)


if __name__=="__main__":
    unittest.main()
