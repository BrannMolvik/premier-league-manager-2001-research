"""Native original choice belongs to exact group or fallback source."""
import unittest
from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_player_name_source import (
    OriginalSupportStaffNameSourceError,
    source_support_staff_name_from_observed_player_pair,
)


def player(index,first,last):
    return Player(index,first,last,0,0,None,0,0,0,(0,0,0),(),())


class SourceSupportStaffNameTests(unittest.TestCase):
    def setUp(self):
        self.players=(player(0,"David","Seaman"),
                      player(1,"Lee","Dixon"),
                      player(2,"Nigel","Winterburn"))
        self.group=OriginalNameGroupCandidateRoute(
            1,1,11,"filtered_nationality_players",(0,2),3)
        self.fallback=OriginalNameGroupCandidateRoute(
            2,2,1,"global_players",(),3)

    def test_two_independent_original_player_name_indices(self):
        result=source_support_staff_name_from_observed_player_pair(
            self.players,self.group,original_first_player_position=0,
            original_surname_player_position=2)
        self.assertEqual(result.full_name,"David Winterburn")
        self.assertEqual(
            source_support_staff_name_from_observed_player_pair(
                self.players,self.fallback,original_first_player_position=0,
                original_surname_player_position=1).full_name,"David Dixon")

    def test_source_filtered_group_rejects_outside_player_even_if_record_exists(self):
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError,"eligible"):
            source_support_staff_name_from_observed_player_pair(
                self.players,self.group,original_first_player_position=0,
                original_surname_player_position=1)
        self.assertEqual(source_support_staff_name_from_observed_player_pair(
            self.players,self.fallback,original_first_player_position=1,
            original_surname_player_position=1).full_name,"Lee Dixon")

    def test_original_dash_requires_retry_not_invented_second_name(self):
        records=(player(0,"-","Seaman"),self.players[1],self.players[2])
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError,"another native draw"):
            source_support_staff_name_from_observed_player_pair(
                records,self.group,original_first_player_position=0,
                original_surname_player_position=2)

    def test_source_index_order_type_and_encoding_fail_closed(self):
        for x,y in ((-1,0),(0,3),(True,0),(0,None),(1.0,2)):
            with self.subTest(x=x,y=y):
                with self.assertRaises(OriginalSupportStaffNameSourceError):
                    source_support_staff_name_from_observed_player_pair(
                        self.players,self.fallback,
                        original_first_player_position=x,
                        original_surname_player_position=y)
        with self.assertRaises(TypeError):
            source_support_staff_name_from_observed_player_pair(
                self.players,None,original_first_player_position=0,
                original_surname_player_position=0)
        with self.assertRaises(OriginalSupportStaffNameSourceError):
            source_support_staff_name_from_observed_player_pair(
                self.players[:2],self.fallback,
                original_first_player_position=0,
                original_surname_player_position=1)
        malformed=(player(0,"山田","Seaman"),self.players[1],self.players[2])
        with self.assertRaisesRegex(OriginalSupportStaffNameSourceError,"CP1252"):
            source_support_staff_name_from_observed_player_pair(
                malformed,self.group,original_first_player_position=0,
                original_surname_player_position=2)


if __name__=="__main__":
    unittest.main()
