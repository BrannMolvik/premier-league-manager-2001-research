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



class SourceOriginal407220Mode4NullOwnerTests(unittest.TestCase):
    @staticmethod
    def team(ids=tuple(range(51,62)),key=7):
        return SourceOriginal406BE0RosterCountTests.team(ids,key)

    @staticmethod
    def player(pid,club=7,active=True,status=2):
        return SourceOriginal406BE0RosterCountTests.player(
            pid,club=club,active=active,status=status)

    def project(self,team,players,ecx=0):
        from original_native_407220_mode4_zero_owner import (
            source_original_407220_mode4_with_null_407ec0)
        return source_original_407220_mode4_with_null_407ec0(
            original_team_record=team,
            original_global_875640_player_array_address=0x40000000,
            original_ordered_player_records=players,
            original_reached_407ec0_return_eax=ecx)

    def composed(self,team,players,ecx=0,name_byte=0x41):
        from original_native_407220_mode4_zero_owner import (
            source_original_407770_arg1_full_counts_with_null_407ec0)
        return source_original_407770_arg1_full_counts_with_null_407ec0(
            original_team_record=team,
            original_global_875640_player_array_address=0x40000000,
            original_ordered_player_records=players,
            original_reached_407ec0_return_eax=ecx,
            original_team_name_first_byte_if_reached=name_byte)

    def test_41fab0_signed_full_team_key_mode4_and_bit4_exact_count(self):
        ids=(51,52,53)
        records=(self.player(51,status=1),self.player(52,active=False,status=None),
                 self.player(53,club=8,status=None))
        r=self.project(self.team(ids),records)
        self.assertEqual(r.original_return_edi_count,1)
        self.assertEqual(r.source_reached_41fab0_ids,ids)
        self.assertEqual(r.source_eligible_41fab0_ids,(51,))
        self.assertFalse(r.native_41fab0_executed)
        self.assertFalse(r.live_game_state_modified)
        x=self.project(self.team((51,),key=0xffffffff),
                       (self.player(51,club=-1,status=2),))
        self.assertEqual(x.original_return_edi_count,1)

    def test_reached_null_owner_all_eleven_counts_then_role_exactly_one(self):
        ids=tuple(range(51,62))
        ps=tuple(self.player(pid,status=1 if i==0 else 2)
                 for i,pid in enumerate(ids))
        x=self.composed(self.team(ids),ps)
        self.assertEqual(x.original_407220_mode4_count.original_return_edi_count,11)
        self.assertEqual(x.original_406be0_role_one_count.source_return_eax,1)
        self.assertTrue(x.original_407770_arg1_receipt.original_return_eax_nonzero)
        self.assertFalse(x.original_live_game_state_modified)
        # 11 selected but TWO source status1 records fails exact 406BE0 EAX==1.
        twice=tuple(self.player(pid,status=1 if i<2 else 2)
                    for i,pid in enumerate(ids))
        self.assertFalse(self.composed(self.team(ids),twice)
                         .original_407770_arg1_receipt.original_return_eax_nonzero)
        # 10 qualified with one source bit4 clear does not reach 407770 EDI==11.
        ten=tuple(self.player(pid,active=(i!=5),status=None if i==5 else (
                    1 if i==0 else 2)) for i,pid in enumerate(ids))
        self.assertEqual(self.composed(self.team(ids),ten)
                         .original_407220_mode4_count.original_return_edi_count,10)
        self.assertFalse(self.composed(self.team(ids),ten)
                         .original_407770_arg1_receipt.original_return_eax_nonzero)

    def test_null_owner_paths_are_explicitly_bounded(self):
        from original_native_407220_mode4_zero_owner import Original407220SourceError
        ids=tuple(range(51,62))
        recs=tuple(self.player(pid,status=1 if i==0 else 2)
                   for i,pid in enumerate(ids))
        good=self.team(ids)
        for changed in (
            dict(ecx=1),
            dict(ecx=True),
            dict(ecx=-1),
            dict(name_byte=0x21),
        ):
            with self.subTest(change=changed),self.assertRaises(Original407220SourceError):
                self.composed(good,recs,**changed)
        not_managed=bytearray(good);not_managed[0x74]=2
        with self.assertRaises(Original407220SourceError):
            self.composed(bytes(not_managed),recs)
        with self.assertRaises(Original407220SourceError):
            self.composed(self.team((51,)),(self.player(51),))
        with self.assertRaises(Original407220SourceError):
            self.project(good,recs[:-1])
        badids=list(recs);badids[0]=self.player(52)
        with self.assertRaises(Original407220SourceError):
            self.project(good,tuple(badids))
        with self.assertRaises(Original407220SourceError):
            self.project(good,recs,ecx=0xffffffff)
        with self.assertRaises(Original407220SourceError):
            self.project(good,tuple(badids),ecx=0)

    def test_original_407220_41fab0_source_opcodes_optional_PE(self):
        p=os.environ.get("FM2001_ORIGINAL_EXE")
        if not p:self.skipTest("private original canonical PE unavailable")
        from hashlib import sha256
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x407220:"83 ec 18",
            0x407229:"8b 83 94 02 00 00",
            0x40723b:"8d 83 44 02 00 00",
            0x407251:"66 8b 01",
            0x40725a:"8b 15 40 56 87 00",
            0x40726e:"e8 3d 88 01 00",
            0x407273:"85 c0",
            0x40727b:"b8 01 00 00 00",
            0x407280:"8b cf",
            0x407282:"d3 e0",
            0x407284:"85 46 14",
            0x407291:"85 c9",
            0x407293:"74 78",
            0x40730d:"45",
            0x407331:"8b c5",
            0x41fab0:"8b 54 24 0c",
            0x41fab7:"0f bf 48 10",
            0x41fabb:"3b d1",
            0x41fac7:"83 fa 04",
            0x41facc:"33 c0",
            0x41faf2:"85 d2",
            0x41faf6:"be 01 00 00 00",
            0x41fafd:"8b 50 14",
            0x41fb00:"d3 e6",
            0x41fb02:"85 f2",
        }
        for va,signature in sites.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(signature)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bs)],bs)



class SourceOriginal510CD0SelectionArrayTests(unittest.TestCase):
    @staticmethod
    def team(ids,key=7):
        return SourceOriginal406BE0RosterCountTests.team(ids,key)

    @staticmethod
    def player(pid,flags14,club=7):
        from original_native_406be0_roster_count import SourceOriginal406BE0Player
        base=SourceOriginal406BE0RosterCountTests.player(
            pid,club=club,active=False,status=None)
        b=bytearray(base.original_player_record_bytes)
        pack_into("<I",b,0x14,flags14)
        return SourceOriginal406BE0Player(
            pid,base.original_player_record_native_pointer,bytes(b),None)

    @staticmethod
    def source_sorted_receipt(team,players,role_penalties=None):
        from original_native_405a20_sort_roster import (
            source_original_405a20_sort_team_roster_by_417e20)
        from original_native_406be0_roster_count import SourceOriginal406BE0Player
        reached=[]
        for r in players:
            raw=bytearray(r.original_player_record_bytes)
            pack_into("<I",raw,0x248,0x50000000+r.original_roster_word_id*4)
            reached.append(SourceOriginal406BE0Player(
                r.original_roster_word_id,r.original_player_record_native_pointer,
                bytes(raw),bytes((0,0,0,1))))
        table=bytearray(32*20)
        for role,penalty in (role_penalties or {}).items():
            table[role*20+16]=penalty
        return source_original_405a20_sort_team_roster_by_417e20(
            original_team_at_405a20=team,
            original_global_875640_player_base=0x40000000,
            original_ordered_player_records=tuple(reached),
            original_874b68_role_table=bytes(table))

    def project(self,team,players,target=0x4):
        from original_native_510cd0_selected_roster import (
            source_original_510cd0_selected_player_pointers)
        return source_original_510cd0_selected_player_pointers(
            original_team_record=team,
            original_global_875640_player_array_address=0x40000000,
            original_ordered_player_records=players,
            original_target_processing_context_offset=target)

    def test_510cd0_retains_order_and_both_bit4_bit5_without_duplicate(self):
        ids=(51,52,53,54,55,56)
        recs=(self.player(51,0x10),self.player(52,0x20),
              self.player(53,0x30),self.player(54,0),
              self.player(55,0x20,club=8),self.player(56,0x20))
        x=self.project(self.team(ids),recs)
        self.assertEqual(x.source_selected_player_pointers,
            tuple(0x40000000+pid*0x250 for pid in (51,52,53,56)))
        self.assertEqual(x.source_selection_count_return_eax,4)
        self.assertEqual(x.source_reached_417f50_player_ids,ids)
        self.assertEqual(x.source_reached_417f60_player_ids,(52,54,55,56))
        self.assertEqual(x.source_select_bit4_or_bit5_player_ids,(51,52,53,56))
        self.assertEqual(x.source_original_target_context_offset,4)
        self.assertEqual(x.source_original_count_context_offset,0x5A4)
        self.assertFalse(x.original_510cd0_was_executed)
        self.assertFalse(x.saved_game_state_modified)

    def test_5111a0_two_source_arrays_use_distinct_5b4_second_slots(self):
        from original_native_510cd0_selected_roster import (
            source_original_5111a0_two_source_selection_arrays)
        first_ids=(51,52,53)
        second_ids=(61,62,63)
        first=(self.player(51,0x10),self.player(52,0),self.player(53,0x20))
        second=(self.player(61,0x30),self.player(62,0),self.player(63,0x10))
        x=source_original_5111a0_two_source_selection_arrays(
            original_match_record=native_match(0x7C4C24),
            original_first_407770_zero_gate_nonzero=True,
            original_second_407770_zero_gate_nonzero=True,
            original_first_405a20_source_sort=self.source_sorted_receipt(
                self.team(first_ids),first),
            original_second_405a20_source_sort=self.source_sorted_receipt(
                self.team(second_ids),second),
            original_global_875640_player_array_address=0x40000000)
        self.assertEqual(x.original_match_vtable,0x7C4C24)
        self.assertEqual(x.source_first_team_receipt.source_original_count_context_offset,0x5A4)
        self.assertEqual(x.source_second_team_receipt.source_original_target_context_offset,0x5B4)
        self.assertEqual(x.source_second_team_receipt.source_original_count_context_offset,0xB54)
        self.assertEqual(x.source_first_team_receipt.source_selection_count_return_eax,2)
        self.assertEqual(x.source_second_team_receipt.source_selection_count_return_eax,2)
        self.assertEqual(x.source_first_team_receipt.source_select_bit4_or_bit5_player_ids,(51,53))
        self.assertEqual(x.source_second_team_receipt.source_select_bit4_or_bit5_player_ids,(61,63))
        self.assertFalse(x.original_5111a0_other_callbacks_executed)
        self.assertFalse(x.original_match_executed)

    def test_rejected_unvisited_original_510cd0_inputs(self):
        from original_native_510cd0_selected_roster import Original510CD0SourceError
        ids=(51,52)
        good=(self.player(51,0x10),self.player(52,0x20))
        for bad_team,players,target in (
            (self.team(ids),good,0x5A4),
            (self.team(ids),good[:1],4),
            (self.team(ids),good+(self.player(53,0x20),),4),
            (self.team(ids),(self.player(52,0x20),self.player(51,0x10)),4),
            (self.team(ids),(self.player(51,0x10),self.player(52,0x20)),True),
        ):
            with self.subTest(target=target,size=len(players)),self.assertRaises(
                    Original510CD0SourceError):
                self.project(bad_team,players,target)
        large=bytearray(self.team(ids))
        pack_into("<i",large,0x294,361)
        with self.assertRaises(Original510CD0SourceError):
            self.project(bytes(large),good)
        from original_native_510cd0_selected_roster import (
            source_original_5111a0_two_source_selection_arrays)
        for first,second in ((False,True),(True,False),(True,None)):
            with self.subTest(first=first,second=second),self.assertRaises(
                    Original510CD0SourceError):
                source_original_5111a0_two_source_selection_arrays(
                    original_match_record=native_match(0x7C4C24),
                    original_first_407770_zero_gate_nonzero=first,
                    original_second_407770_zero_gate_nonzero=second,
                    original_first_405a20_source_sort=self.source_sorted_receipt(
                        self.team(ids),good),
                    original_second_405a20_source_sort=self.source_sorted_receipt(
                        self.team(ids),good),
                    original_global_875640_player_array_address=0x40000000)

    def test_source_405a20_order_descending_tier_and_stable_on_ties(self):
        ids=(51,52,53,54,55,56)
        rows=(self.player(51,0x20),self.player(52,0x10),
              self.player(53,0x10),self.player(54,0),
              self.player(55,0x20),self.player(56,0x30))
        first=self.source_sorted_receipt(self.team(ids),rows)
        self.assertEqual(first.source_player_ids_after,(52,53,56,51,55,54))
        self.assertEqual(first.source_player_score_pairs_before,
            ((51,3000),(52,4000),(53,4000),(54,0),(55,3000),(56,4000)))
        self.assertFalse(first.original_405a20_executed)
        self.assertFalse(first.original_game_state_modified)
        x=self.project(first.source_projected_team_after_405a20,
                       first.original_player_records_sorted_for_510cd0)
        self.assertEqual(x.source_select_bit4_or_bit5_player_ids,(52,53,56,51,55))
        second=self.source_sorted_receipt(self.team(ids),rows,
                                         role_penalties={1:12})
        self.assertEqual(second.source_player_score_pairs_before,
            tuple((pid,score-12) for pid,score in first.source_player_score_pairs_before))
        self.assertEqual(second.source_player_ids_after,first.source_player_ids_after)

    def test_source_405a20_rejects_untrusted_table_or_player_identity(self):
        from original_native_405a20_sort_roster import (
            source_original_405a20_sort_team_roster_by_417e20 as rank,
            Original405A20SourceError)
        ids=(51,52)
        players=(self.player(51,0x10),self.player(52,0x20))
        good=self.source_sorted_receipt(self.team(ids),players)
        self.assertEqual(len(good.original_player_records_sorted_for_510cd0),2)
        base=dict(original_team_at_405a20=self.team(ids),
                  original_global_875640_player_base=0x40000000,
                  original_ordered_player_records=good.original_player_records_sorted_for_510cd0,
                  original_874b68_role_table=bytes(32*20))
        for k,v in (
            ("original_874b68_role_table",bytes(10)),
            ("original_global_875640_player_base",0),
            ("original_ordered_player_records",()),
            ("original_ordered_player_records",tuple(reversed(
                good.original_player_records_sorted_for_510cd0))),
        ):
            with self.subTest(field=k),self.assertRaises(Original405A20SourceError):
                rank(**(base|{k:v}))
        from original_native_510cd0_selected_roster import (
            source_original_5111a0_two_source_selection_arrays)
        with self.assertRaises(Original510CD0SourceError):
            source_original_5111a0_two_source_selection_arrays(
                original_match_record=native_match(0x7C4C24),
                original_first_407770_zero_gate_nonzero=True,
                original_second_407770_zero_gate_nonzero=True,
                original_first_405a20_source_sort=None,
                original_second_405a20_source_sort=good,
                original_global_875640_player_array_address=0x40000000)

    def test_original_405a20_stable_descending_sort_and_417e20_pe_signatures(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("private canonical original PE optional in CI")
        from hashlib import sha256
        raw=Path(original).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x511235:"e8 e6 47 ef ff",0x51125e:"e8 bd 47 ef ff",
            0x405a20:"8b 44 24 08",0x405a29:"8b 81 94 02 00 00",
            0x405a38:"e8 73 fe ff ff",
            0x4058b0:"83 ec 18",0x4058e1:"e8 ca ff ff ff",
            0x40595e:"66 8b 01",0x405966:"ff 12",0x405968:"85 c0",
            0x40596a:"74 18",0x405974:"66 8b 17",
            0x405984:"8b 44 24 18",0x405990:"83 c0 02",
            0x40b4a0:"8b 44 24 04",0x40b4c9:"8b 57 04",
            0x40b4cd:"e8 4e c9 00 00",0x40b4da:"e8 41 c9 00 00",
            0x40b4e1:"3b c3",0x40b4e3:"0f 9c c1",
            0x417e20:"53",0x417e2c:"e8 af 00 00 00",
            0x417e3f:"e8 bc 00 00 00",0x417e52:"e8 49 00 00 00",
            0x417e65:"e8 56 00 00 00",0x417e73:"8b 8e 48 02 00 00",
            0x417e79:"e8 42 25 0d 00",0x417e84:"8d 04 80",
            0x417e89:"8a 54 81 10",0x417e94:"2b c2",
            0x7bef9c:"a0 b4 40 00",
        }
        for va,hexbytes in sites.items():
            with self.subTest(va=hex(va)):
                signature=bytes.fromhex(hexbytes)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(signature)],signature)

    def test_original_510cd0_417f50_417f60_optional_pe_signatures(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("canonical private original PE optional in CI")
        from hashlib import sha256
        raw=Path(original).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        signatures={
            0x510CD0:"83 ec 08",
            0x510CDA:"8b 8f 94 02 00 00",
            0x510CF3:"8d 9f 44 02 00 00",
            0x510CFC:"66 8b 03",
            0x510D05:"a1 40 56 87 00",
            0x510D11:"e8 3a 72 f0 ff",
            0x510D16:"85 c0",
            0x510D1D:"e8 3e 72 f0 ff",
            0x510D26:"8b 4c 24 10",
            0x510D2A:"89 75 00",
            0x510D4B:"8b 44 24 10",
            0x417F50:"8b 44 24 04",
            0x417F54:"8b 40 04",
            0x417F58:"e8 83 ff ff ff",
            0x417F60:"8b 44 24 04",
            0x417F64:"8b 40 04",
            0x417F68:"e8 93 ff ff ff",
            0x417EE0:"0f bf 41 10",
            0x417EEF:"8b 41 14",
            0x417F00:"0f bf 41 10",
            0x417F0F:"8b 41 14",
            0x51126C:"e8 5f fa ff ff",
            0x511277:"89 86 a4 05 00 00",
            0x511287:"e8 44 fa ff ff",
            0x51128C:"89 86 54 0b 00 00",
        }
        for va,hexbytes in signatures.items():
            with self.subTest(va=hex(va)):
                bs=bytes.fromhex(hexbytes)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bs)],bs)



class SourceOriginal5111A0ConditionalBranchTests(unittest.TestCase):
    @staticmethod
    def owner(n=123):
        b=bytearray(0x20);pack_into("<I",b,0x1c,n);return bytes(b)

    @staticmethod
    def match(flags=0,ptr=0x7000):
        r=bytearray(native_match(0x7C9D9C))
        pack_into("<I",r,0x44,flags);pack_into("<I",r,0x4c,ptr)
        return bytes(r)

    @staticmethod
    def context(first=0x10000,second=0x20000):
        b=bytearray(0x5b4)
        pack_into("<I",b,0,first);pack_into("<I",b,0x5b0,second)
        return bytes(b)

    @staticmethod
    def team(ids=tuple(range(51,62)),key=7):
        return SourceOriginal406BE0RosterCountTests.team(ids,key)

    def kwargs(self,flags=0):
        return dict(
            original_match_record_at_5111a0=self.match(flags),
            original_processing_context_at_5111a0=self.context(),
            original_first_team_record_at_5111a0=self.team(key=7),
            original_second_team_record_at_5111a0=self.team(tuple(range(71,82)),key=8),
            original_first_match_4c_pointer_if_nonhuman_reached=None,
            original_second_match_4c_pointer_if_nonhuman_reached=None,
            original_first_match_4c_owner_record_if_nonhuman_reached=None,
            original_second_match_4c_owner_record_if_nonhuman_reached=None,
            original_first_4037b0_human_al_if_reached=None,
            original_second_4037b0_human_al_if_reached=None,
            original_first_511170_v18_nonzero_if_needed=None,
            original_second_511170_v18_nonzero_if_needed=None,
            original_first_511170_second_4f3dc0_pointer_if_needed=None,
            original_second_511170_second_4f3dc0_pointer_if_needed=None,
        )

    def project(self,args):
        from original_native_5111a0_conditional_prep import (
            source_original_5111a0_conditional_nonhuman_409b50_plan)
        return source_original_5111a0_conditional_nonhuman_409b50_plan(**args)

    def test_completed_match_bit5_skips_both_nonhuman_updates_but_not_sorts(self):
        x=self.project(self.kwargs(0x20))
        self.assertTrue(x.original_409b50_skipped_due_to_bit5)
        self.assertEqual(x.source_mandatory_405a20_order,(0x10000,0x20000))
        self.assertEqual(tuple(s.original_409b50_reached_args_if_needed
                               for s in x.original_side_conditional_receipts),(None,None))
        self.assertFalse(x.original_all_5111a0_callbacks_executed)
        self.assertFalse(x.live_world_modified)

    def test_first_human_skips_and_second_nonhuman_v18_false_pushes_zero(self):
        x=self.kwargs()
        x.update(original_first_4037b0_human_al_if_reached=True,
                 original_second_4037b0_human_al_if_reached=False,
                 original_second_match_4c_pointer_if_nonhuman_reached=0x7000,
                 original_second_match_4c_owner_record_if_nonhuman_reached=self.owner(0xBABE),
                 original_second_511170_v18_nonzero_if_needed=False)
        r=self.project(x)
        self.assertEqual(r.original_side_conditional_receipts[0]
                         .original_409b50_reached_args_if_needed,None)
        self.assertEqual(r.original_side_conditional_receipts[1]
                         .original_409b50_reached_args_if_needed,(0,11,0xBABE))
        self.assertFalse(r.original_side_conditional_receipts[1].native_409b50_executed)

    def test_first_nonhuman_can_mutate_second_native_match_owner(self):
        x=self.kwargs()
        x.update(original_first_4037b0_human_al_if_reached=False,
                 original_second_4037b0_human_al_if_reached=False,
                 original_first_match_4c_pointer_if_nonhuman_reached=0x7000,
                 original_second_match_4c_pointer_if_nonhuman_reached=0x8000,
                 original_first_match_4c_owner_record_if_nonhuman_reached=self.owner(111),
                 original_second_match_4c_owner_record_if_nonhuman_reached=self.owner(222),
                 original_first_511170_v18_nonzero_if_needed=False,
                 original_second_511170_v18_nonzero_if_needed=True,
                 original_second_511170_second_4f3dc0_pointer_if_needed=0xA000)
        r=self.project(x)
        sides=r.original_side_conditional_receipts
        self.assertEqual(sides[0].original_409b50_reached_args_if_needed,(0,11,111))
        self.assertEqual(sides[1].original_409b50_reached_args_if_needed,(0xA000,11,222))
        self.assertEqual(tuple(s.original_4037b0_human_al_if_reached for s in sides),
                         (False,False))

    def test_unreached_callback_facts_and_unsupported_owner_fail_closed(self):
        from original_native_5111a0_conditional_prep import Original5111A0ConditionalSourceError
        good=self.kwargs()
        good.update(original_first_4037b0_human_al_if_reached=True,
                    original_second_4037b0_human_al_if_reached=True)
        for fields in (
            dict(original_first_511170_v18_nonzero_if_needed=False),
            dict(original_first_511170_second_4f3dc0_pointer_if_needed=0x1234),
            dict(original_first_match_4c_pointer_if_nonhuman_reached=0x7000),
            dict(original_first_match_4c_owner_record_if_nonhuman_reached=self.owner()),
            dict(original_first_4037b0_human_al_if_reached=1),
            dict(original_match_record_at_5111a0=bytes(0x58)),
            dict(original_processing_context_at_5111a0=self.context(first=0,second=1)),
            dict(original_processing_context_at_5111a0=self.context(first=2,second=2)),
            dict(original_first_team_record_at_5111a0=b""),
        ):
            with self.subTest(fields=str(fields)[:100]),self.assertRaises(Original5111A0ConditionalSourceError):
                self.project(good|fields)
        x=self.kwargs()
        x.update(original_first_4037b0_human_al_if_reached=False,
                 original_second_4037b0_human_al_if_reached=True,
                 original_first_match_4c_pointer_if_nonhuman_reached=0x7000,
                 original_first_match_4c_owner_record_if_nonhuman_reached=self.owner(),
                 original_first_511170_v18_nonzero_if_needed=True)
        for fields in (
            dict(original_first_511170_second_4f3dc0_pointer_if_needed=None),
            dict(original_first_511170_second_4f3dc0_pointer_if_needed=0),
            dict(original_first_match_4c_pointer_if_nonhuman_reached=0x8000),
        ):
            with self.subTest(fields=fields),self.assertRaises(Original5111A0ConditionalSourceError):
                self.project(x|fields)
        x=self.kwargs(0x20)
        x["original_first_4037b0_human_al_if_reached"]=False
        with self.assertRaises(Original5111A0ConditionalSourceError):
            self.project(x)

    def test_source_join_5111a0_conditional_two_sorts_and_both_selected_arrays(self):
        from original_native_5111a0_conditional_prep import (
            source_original_5111a0_conditional_sorts_and_selected_tail as compose,
            Original5111A0ConditionalSourceError)
        cargs=self.kwargs(0x20) # original bit5 skips 409B50 but sorts are mandatory
        c=self.project(cargs)
        util=SourceOriginal510CD0SelectionArrayTests
        first_ids=tuple(range(51,62))
        second_ids=tuple(range(71,82))
        first=util.source_sorted_receipt(
            util.team(first_ids,key=7),
            tuple(util.player(pid,0x10 if i==0 else 0x20)
                  for i,pid in enumerate(first_ids)))
        second=util.source_sorted_receipt(
            util.team(second_ids,key=8),
            tuple(util.player(pid,0x10 if i==1 else 0x20,club=8)
                  for i,pid in enumerate(second_ids)))
        args=dict(
            original_conditional_source=c,
            original_native_match_record_at_entry=cargs["original_match_record_at_5111a0"],
            original_processing_context_at_entry=cargs["original_processing_context_at_5111a0"],
            original_first_team_native_pointer_at_405a20=0x10000,
            original_second_team_native_pointer_at_405a20=0x20000,
            original_first_team_record_actual_at_405a20=first.original_team_roster_before_405a20,
            original_second_team_record_actual_at_405a20=second.original_team_roster_before_405a20,
            original_first_405a20_source_sort=first,
            original_second_405a20_source_sort=second,
            original_global_875640_player_array_address=0x40000000,
            original_first_407770_zero_gate_nonzero=True,
            original_second_407770_zero_gate_nonzero=True,
        )
        result=compose(**args)
        self.assertEqual(result.original_reached_action_sites_in_order,
                         (0x511235,0x51125E,0x51126C,0x511287))
        self.assertEqual(result.two_selected_pointer_arrays
                         .source_first_team_receipt.source_select_bit4_or_bit5_player_ids,first_ids)
        self.assertEqual(result.two_selected_pointer_arrays
                         .source_second_team_receipt.source_select_bit4_or_bit5_player_ids,(72,71,*range(73,82)))
        self.assertFalse(result.native_world_and_sort_mutated)
        self.assertFalse(result.original_game_state_modified)
        for changed in (
            {"original_first_team_native_pointer_at_405a20":0x20000},
            {"original_first_407770_zero_gate_nonzero":False},
            {"original_second_405a20_source_sort":first},
            {"original_native_match_record_at_entry":self.match(0)},
            {"original_processing_context_at_entry":self.context(0x99999,0x20000)},
            {"original_global_875640_player_array_address":0},
        ):
            with self.subTest(changed=str(changed)[:95]),self.assertRaises(
                    Original5111A0ConditionalSourceError):
                compose(**(args|changed))

    def test_original_511170_5111a0_409b50_source_opcode_sites_if_private(self):
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:self.skipTest("private canonical original PE unavailable in CI")
        from hashlib import sha256
        raw=Path(original).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x511176:"8b 4e 4c",0x511179:"e8 42 2c fe ff",
            0x511182:"ff 52 18",0x511185:"85 c0",
            0x511189:"8b 4e 4c",0x51118c:"e8 2f 2c fe ff",
            0x511194:"8b c7",0x5111ab:"8b 47 44",
            0x5111ae:"c1 e8 05",0x5111b1:"a8 01",
            0x5111b5:"8b 0e",0x5111b7:"e8 f4 25 ef ff",
            0x5111c0:"8b 4f 4c",0x5111cb:"8b 82 94 02 00 00",
            0x5111d2:"e8 99 ff ff ff",0x5111da:"e8 71 89 ef ff",
            0x5111df:"8b 8e b0 05 00 00",0x5111e5:"e8 c6 25 ef ff",
            0x511204:"e8 67 ff ff ff",0x511210:"e8 3b 89 ef ff",
            0x511235:"e8 e6 47 ef ff",0x51125e:"e8 bd 47 ef ff",
            0x4f3dc0:"8b c1",0x4f3dc9:"8b c1",0x409bcb:"e8 c0 00 00 00",
            0x409bd0:"89 be d8 01 00 00",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                signature=bytes.fromhex(hx)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(signature)],signature)


if __name__=="__main__":
    unittest.main()
