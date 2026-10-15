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



if __name__=="__main__":
    unittest.main()
