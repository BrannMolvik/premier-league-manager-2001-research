"""Source club-pointer names are never mistaken for player names."""
import unittest
from dataclasses import replace

from fm2001_data import Club
from original_supportstart_name_group_source import (
    parse_original_static_name_group_tables, source_original_name_group_route,
)
from original_supportstart_club_name_source import (
    OriginalSupportStaffClubNameError, project_original_supportstart_observed_club_name,
)


def fixture_static():
    from struct import pack_into
    data=bytearray(0x25e0)
    pack_into("<I",data,0x4a,209)
    for i in range(209):
        pack_into("<I",data,0x4e+i*43+6,i)
    pack_into("<I",data,0x2369,209)
    for i in range(209):
        pack_into("<BH",data,0x236d+i*3,i,634+i)
    return parse_original_static_name_group_tables(bytes(data),require_original_sha256=False)


class OriginalSupportStaffClubNameTests(unittest.TestCase):
    def setUp(self):
        self.clubs=tuple(
            Club(i,"Club Full "+str(i),"C"+str(i),"Original Ground",0,
                 country_id=1 if i<11 else 26) for i in range(1246)
        )
        table=fixture_static()
        self.route=source_original_name_group_route(
            table,country_index=1,source_clubs=self.clubs,
            original_global_player_count=30064
        )
        self.fallback=source_original_name_group_route(
            table,country_index=0,source_clubs=self.clubs,
            original_global_player_count=30064
        )

    def test_real_native_club_fields_are_first_name_and_short_name(self):
        projected=project_original_supportstart_observed_club_name(
            self.clubs,self.route,
            original_first_club_position=0,
            original_second_club_position=5,
        )
        self.assertEqual(projected.full_name,"Club Full 0 C5")
        self.assertEqual((projected.first_source_club_position,
                          projected.second_source_club_position),(0,5))
        self.assertEqual(self.route.original_group_club_count,11)

    def test_small_source_group_rejects_club_projection_and_foreign_indices(self):
        with self.assertRaisesRegex(OriginalSupportStaffClubNameError,"no qualified"):
            project_original_supportstart_observed_club_name(
                self.clubs,self.fallback,original_first_club_position=0,
                original_second_club_position=5)
        for idx in (-1,11,1246,True,1.5,None):
            with self.subTest(index=idx):
                with self.assertRaises(OriginalSupportStaffClubNameError):
                    project_original_supportstart_observed_club_name(
                        self.clubs,self.route,original_first_club_position=0,
                        original_second_club_position=idx)
        bad=list(self.clubs)
        bad[5]=replace(bad[5],index=42)
        with self.assertRaises(OriginalSupportStaffClubNameError):
            project_original_supportstart_observed_club_name(
                tuple(bad),self.route,original_first_club_position=0,
                original_second_club_position=5)

    def test_original_source_name_text_fails_closed_on_missing_or_invalid(self):
        bad=list(self.clubs)
        bad[0]=replace(bad[0],name="-")
        with self.assertRaisesRegex(OriginalSupportStaffClubNameError,"retry"):
            project_original_supportstart_observed_club_name(
                tuple(bad),self.route,
                original_first_club_position=0,original_second_club_position=5)
        bad[0]=replace(bad[0],name="😀")
        with self.assertRaisesRegex(OriginalSupportStaffClubNameError,"CP1252"):
            project_original_supportstart_observed_club_name(
                tuple(bad),self.route,
                original_first_club_position=0,original_second_club_position=5)


if __name__=="__main__":
    unittest.main()
