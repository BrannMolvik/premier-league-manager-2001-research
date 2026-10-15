"""Original 403E10 competition sentinel and 409B50 +1D8 lifecycle tests."""
import os,unittest
from hashlib import sha256
from pathlib import Path
from struct import pack_into,unpack_from
from original_native_409b50_division_owner import (
    Original409B50SourceError,
    source_original_403e10_competition_owner_gate as gate,
    source_original_409b50_select_edi_and_write_team_plus1d8 as write,
)


def source_team(owner_index=2,score=17):
    b=bytearray(0x298)
    pack_into("<I",b,4,7)
    pack_into("<I",b,0x40,owner_index)
    pack_into("<I",b,0x34,score)
    pack_into("<I",b,0x1d8,9999)
    return bytes(b)


def indexed(remaining=2):
    b=bytearray(0x40)
    b[0x20]=33
    b[0x21]=44
    b[0x22]=55
    pack_into("<I",b,0x24,remaining)
    return bytes(b)


class Original409B50OwnerWorldTests(unittest.TestCase):
    def owner(self,t=None,rec=None,base=0x800000):
        t=t if t is not None else source_team()
        if unpack_from("<I",t,0x40)[0]==0xffffffff:
            return gate(original_native_team_pointer=0x500000,
                original_native_team_record_before_403e10=t)
        return gate(original_native_team_pointer=0x500000,
            original_native_team_record_before_403e10=t,
            original_global_875628_base_if_index_reached=base,
            original_global_875628_indexed_record_if_reached=rec or indexed())

    def apply(self,owner,mode=None,rec=None,post=None,ptr=0x500000):
        if post is None:post=owner.original_source_team_after_optional_plus40_write
        return write(original_403e10_owner_gate=owner,
            original_reached_409500_return_eax_if_403e10_true=mode,
            original_reached_875628_indexed_record_at_409b72_if_valid_mode=rec,
            original_native_team_pointer_post_409c90=ptr,
            original_native_team_record_post_409c90_pre_409bd0=post)

    def test_403e10_reached_global_sentinel_resets_club40_and_skips_409500(self):
        x=self.owner(rec=indexed(0xffffffff))
        self.assertFalse(x.original_return_eax_nonzero)
        self.assertEqual(unpack_from("<I",x.original_source_team_after_optional_plus40_write,0x40)[0],0xffffffff)
        self.assertEqual(unpack_from("<I",x.original_team_record_before,0x40)[0],2)
        self.assertFalse(x.native_403e10_executed)
        self.assertFalse(x.live_world_mutated)
        y=self.apply(x)
        self.assertTrue(y.original_409b50_409c90_called_unconditionally)
        self.assertEqual(y.original_409b50_selected_edi_dword_for_409c90,0)
        self.assertEqual(unpack_from("<I",y.original_native_team_after_409bd0_literal_store,0x1d8)[0],0)
        self.assertFalse(y.native_409c90_executed)

    def test_403e10_team_plus40_already_sentinel_skips_table_byte_and_mutation(self):
        x=self.owner(source_team(0xffffffff))
        self.assertFalse(x.original_return_eax_nonzero)
        self.assertEqual(x.original_source_team_after_optional_plus40_write,x.original_team_record_before)
        y=self.apply(x)
        self.assertEqual(y.original_409b50_selected_edi_dword_for_409c90,0)

    def test_409b50_409500_source_four_way_jumptable_and_unsigned_default(self):
        x=self.owner()
        self.assertTrue(x.original_return_eax_nonzero)
        self.assertEqual(unpack_from("<I",x.original_source_team_after_optional_plus40_write,0x40)[0],2)
        for mode,offset,value in ((0,0x20,33),(1,0x22,55),
                                  (2,0x20,33),(3,0x21,44),
                                  (0xffffffff,None,0)):
            with self.subTest(mode=mode):
                rec=indexed() if offset is not None else None
                y=self.apply(x,mode=mode,rec=rec)
                self.assertEqual(y.original_409b50_source_indexed_byte_offset_if_reached,offset)
                self.assertEqual(y.original_409b50_selected_edi_dword_for_409c90,value)
                self.assertEqual(unpack_from("<I",y.original_native_team_after_409bd0_literal_store,0x1d8)[0],value)
                self.assertFalse(y.native_409500_executed)
                self.assertFalse(y.native_409bd0_executed)

    def test_original_409c90_mutable_team_snapshot_is_independent_and_preserved(self):
        x=self.owner()
        later=bytearray(x.original_source_team_after_optional_plus40_write)
        pack_into("<I",later,0x34,481)
        pack_into("<I",later,0x1dc,773)
        y=self.apply(x,mode=3,rec=indexed(),post=bytes(later))
        self.assertEqual(unpack_from("<I",y.original_native_team_after_409bd0_literal_store,0x34)[0],481)
        self.assertEqual(unpack_from("<I",y.original_native_team_after_409bd0_literal_store,0x1dc)[0],773)
        self.assertEqual(unpack_from("<I",y.original_native_team_after_409bd0_literal_store,0x1d8)[0],44)
        self.assertEqual(unpack_from("<I",y.original_native_team_at_post_409c90_before_store,0x1d8)[0],9999)
        self.assertFalse(y.original_live_game_state_mutated)

    def test_native_owner_and_unvisited_409500_results_fail_closed(self):
        good=self.owner()
        for changed in (
            dict(original_reached_409500_return_eax_if_403e10_true=None),
            dict(original_reached_409500_return_eax_if_403e10_true=True),
            dict(original_reached_409500_return_eax_if_403e10_true=0,original_reached_875628_indexed_record_at_409b72_if_valid_mode=None),
            dict(original_reached_409500_return_eax_if_403e10_true=0xffffffff,original_reached_875628_indexed_record_at_409b72_if_valid_mode=indexed()),
            dict(original_native_team_pointer_post_409c90=0x500001),
            dict(original_native_team_record_post_409c90_pre_409bd0=bytes(8)),
        ):
            with self.subTest(fields=str(changed)[:100]),self.assertRaises(Original409B50SourceError):
                write(**(dict(original_403e10_owner_gate=good,
                    original_reached_409500_return_eax_if_403e10_true=0,
                    original_reached_875628_indexed_record_at_409b72_if_valid_mode=indexed(),
                    original_native_team_pointer_post_409c90=0x500000,
                    original_native_team_record_post_409c90_pre_409bd0=source_team())|changed))
        no=self.owner(source_team(0xffffffff))
        for changed in (dict(original_reached_409500_return_eax_if_403e10_true=0),
                        dict(original_reached_875628_indexed_record_at_409b72_if_valid_mode=indexed())):
            with self.assertRaises(Original409B50SourceError):
                write(**(dict(original_403e10_owner_gate=no,
                    original_reached_409500_return_eax_if_403e10_true=None,
                    original_reached_875628_indexed_record_at_409b72_if_valid_mode=None,
                    original_native_team_pointer_post_409c90=0x500000,
                    original_native_team_record_post_409c90_pre_409bd0=source_team(0xffffffff))|changed))
        for params in (
            dict(original_native_team_pointer=0),
            dict(original_native_team_record_before_403e10=bytes(4)),
            dict(original_global_875628_base_if_index_reached=None),
            dict(original_global_875628_indexed_record_if_reached=bytes(8)),
        ):
            with self.subTest(params=params),self.assertRaises(Original409B50SourceError):
                gate(**(dict(original_native_team_pointer=0x500000,
                    original_native_team_record_before_403e10=source_team(),
                    original_global_875628_base_if_index_reached=0x800000,
                    original_global_875628_indexed_record_if_reached=indexed())|params))

    def test_original_private_403e10_409b50_source_pe_opcode_chain(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("canonical original executable private, never in CI")
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x403e10:"8b 41 40",
            0x403e13:"83 ca ff",
            0x403e1b:"8b 35 28 56 87 00",
            0x403e22:"c1 e0 06",
            0x403e25:"8b 7c 30 24",
            0x403e2e:"89 51 40",
            0x403e31:"8b 71 40",
            0x403e39:"0f 95 c0",
            0x409b54:"33 ff",
            0x409b56:"e8 b5 a2 ff ff",
            0x409b61:"e8 9a f9 ff ff",
            0x409b66:"83 f8 03",
            0x409b6b:"ff 24 85 dc 9b 40 00",
            0x409b72:"8b 46 40",
            0x409b80:"8a 4c 10 22",
            0x409b86:"8b 46 40",
            0x409b94:"8a 4c 10 21",
            0x409b9a:"8b 46 40",
            0x409ba8:"8a 4c 10 20",
            0x409bae:"8b 44 24 14",
            0x409bc1:"8b 44 24 18",
            0x409bcb:"e8 c0 00 00 00",
            0x409bd0:"89 be d8 01 00 00",
        }
        for va,h in sites.items():
            with self.subTest(site=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
        self.assertEqual(
            tuple(unpack_from("<I",raw,0x409bdc-0x400000+i*4)[0] for i in range(4)),
            (0x409b9a,0x409b72,0x409b9a,0x409b86))


if __name__=="__main__":
    unittest.main()
