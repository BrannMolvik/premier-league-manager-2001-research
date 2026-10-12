"""Source-validated native name grouping, distinct from country club indexes."""
from struct import pack_into
import unittest

from original_supportstart_name_group_source import (
    OriginalNameGroupError, COUNTRY_COUNT,
    OriginalEligibleNamePlayerPools,
    parse_original_static_name_group_tables,
    original_filtered_name_pool_from_master_core,
    source_original_name_group_route,
)


def static_fixture():
    raw=bytearray(0x25e0)
    pack_into("<I",raw,0x4a,209)
    for i in range(209):
        pack_into("<I",raw,0x4e+i*43+6,i)
    pack_into("<I",raw,0x4e+199*43+6,0xffffffff)
    pack_into("<I",raw,0x2369,209)
    for i in range(209):
        pack_into("<BH",raw,0x236d+3*i,i,634+i)
    return bytes(raw)


def raw_master_core():
    # Retain native source 1246-club section without simulating club grouping.
    players=[("David","Seaman",1)]*11 + [("John","Noah",1),
          ("X.","Smith",1),("John","Nolan",1),("Alan","Doe",2)]
    strings=["David","Seaman","John","Noah","X.","Smith","Nolan","Alan","Doe"]
    payload=b""
    offsets=[]
    for text in strings:
        offsets.append(len(payload))
        payload+=text.encode("cp1252")+b"\0"
    core=pack_data_core(payload,offsets)
    positions={s:i for i,s in enumerate(strings)}
    start=4+1246*181
    master=bytearray(start+4+len(players)*103)
    pack_into("<I",master,0,1246)
    pack_into("<I",master,start,len(players))
    for i,(first,last,nat) in enumerate(players):
        at=start+4+i*103
        pack_into("<HHHHB",master,at,i,positions[first],positions[last],0,nat)
    return bytes(master),core


def pack_data_core(payload,offsets):
    from struct import pack
    return pack("<II",len(payload),len(offsets))+payload+pack("<"+"I"*len(offsets),*offsets)


class OriginalNameGroupTests(unittest.TestCase):
    def setUp(self):
        self.table=parse_original_static_name_group_tables(
            static_fixture(),require_original_sha256=False)
        master,core=raw_master_core()
        self.pools=original_filtered_name_pool_from_master_core(
            master,core,require_original_sha256=False,
            test_expected_player_count=15)

    def test_native_static_country_remaps_and_original_group_headers(self):
        self.assertEqual(self.table.group_records_offset,0x236d)
        self.assertEqual(self.table.resolved_group(199),26)
        self.assertEqual(self.table.resolved_group(1),1)
        self.assertEqual(self.table.serialized_group_label_ids[208],842)

    def test_only_source_eligible_players_join_nationality_buckets(self):
        self.assertEqual(self.pools.global_player_count,15)
        # The 11 David/Seaman entries pass, but surname 'Noah' is
        # excluded both by initial 'N' and second byte 'o'.
        # First name X. is excluded by first[1]=='.'.
        self.assertEqual(self.pools.group_players[1],tuple(range(11)))
        self.assertEqual(self.pools.group_players[2],(14,))
        self.assertEqual(self.pools.filtered_total,12)
        main=source_original_name_group_route(self.table,self.pools,country_index=1)
        self.assertEqual(main.candidate_source,"filtered_nationality_players")
        self.assertEqual(main.source_record_positions,tuple(range(11)))
        self.assertTrue(main.eligible_source_player_position(10))
        self.assertFalse(main.eligible_source_player_position(11))
        fallback=source_original_name_group_route(self.table,self.pools,country_index=2)
        self.assertEqual(fallback.candidate_source,"global_players")
        self.assertEqual(fallback.original_group_eligible_player_count,1)
        self.assertTrue(fallback.eligible_source_player_position(11))
        self.assertEqual(fallback.source_record_positions,())

    def test_source_identity_and_truncated_data_fail_closed(self):
        master,core=raw_master_core()
        with self.assertRaisesRegex(OriginalNameGroupError,"checksum"):
            original_filtered_name_pool_from_master_core(master,core)
        with self.assertRaisesRegex(OriginalNameGroupError,"checksum"):
            parse_original_static_name_group_tables(static_fixture())
        for value in (-1,209,True,None):
            with self.subTest(value=value):
                with self.assertRaises(OriginalNameGroupError):
                    self.table.resolved_group(value)
        with self.assertRaises(OriginalNameGroupError):
            original_filtered_name_pool_from_master_core(
                master[:-2],core,require_original_sha256=False,
                test_expected_player_count=15)
        with self.assertRaises(OriginalNameGroupError):
            original_filtered_name_pool_from_master_core(
                master,core[:-5],require_original_sha256=False,
                test_expected_player_count=15)


if __name__=="__main__":
    unittest.main()
