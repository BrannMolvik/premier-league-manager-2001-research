"""Native 0x42C400 source user name initialization precedes TeamSelect six staff."""
import unittest
from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_user_creation_rng import (
    OriginalSourceUserBirthNameError,
    SOURCE_USER_NAME_PAIR_COUNT,
    SOURCE_USER_NAME_RNG_CALL_COUNT,
    consume_original_user_birth_name_pairs,
)


def player(i, first, last):
    return Player(i,first,last,0,1,None,0,0,0,(0,0,0),(),())


class Recorder:
    def __init__(self, values):
        self.values=list(values)
        self.bounds=[]
    def randbelow(self,bound):
        self.bounds.append(bound)
        return self.values.pop(0)


class NativeUserCreationNameRngTests(unittest.TestCase):
    def setUp(self):
        self.players=(player(0,"-","Seaman"),
                      player(1,"David","Dixon"),
                      player(2,"Nigel","Winterburn"))
        self.route=OriginalNameGroupCandidateRoute(
            26,26,3,"global_players",(),3)

    def test_all_thirteen_pairs_without_sentinel_retry(self):
        values=list(i%3 for i in range(26))
        rng=Recorder(values)
        receipt=consume_original_user_birth_name_pairs(
            rng,self.players,self.route)
        self.assertEqual(len(receipt.source_pairs),SOURCE_USER_NAME_PAIR_COUNT)
        self.assertEqual(receipt.direct_source_rng_call_count,
                         SOURCE_USER_NAME_RNG_CALL_COUNT)
        self.assertEqual(rng.bounds,[3]*26)
        self.assertEqual(rng.values,[])
        first=receipt.source_pairs[0]
        self.assertEqual((first.source_first_player_id,
                          first.source_surname_player_id), (0,1))
        self.assertEqual((first.source_first_text,first.source_surname_text),
                         ("-","Dixon"))
        self.assertEqual(
            (first.first_text_owner_offset,first.surname_text_owner_offset),
            (0x520,0x524)
        )
        self.assertEqual(
            (receipt.source_pairs[8].first_text_owner_offset,
             receipt.source_pairs[8].surname_text_owner_offset),
            (0x560,0x564)
        )
        self.assertEqual(
            [(p.first_text_owner_offset,p.surname_text_owner_offset)
             for p in receipt.source_pairs[9:]],
            [(0x568,0x578),(0x56c,0x57c),(0x570,0x580),(0x574,0x584)]
        )

    def test_existing_filtered_group_has_exact_source_candidate_order(self):
        route=OriginalNameGroupCandidateRoute(
            1,1,11,"filtered_nationality_players",(2,0),3)
        rng=Recorder([1,0]*13)
        receipt=consume_original_user_birth_name_pairs(
            rng,self.players,route)
        self.assertEqual(receipt.source_pairs[0].source_first_player_id,0)
        self.assertEqual(receipt.source_pairs[0].source_surname_player_id,2)
        self.assertEqual(rng.bounds,[2]*26)

    def test_input_rejection_does_not_advance_shared_crt(self):
        for rows,route in (
            ((),self.route),
            ((player(1,"David","Dixon"),),self.route),
            (self.players,OriginalNameGroupCandidateRoute(
                1,1,0,"global_players",(),4)),
            (self.players,OriginalNameGroupCandidateRoute(
                1,1,11,"filtered_nationality_players",(9,),3)),
            ((player(0,"","Seaman"),)+self.players[1:],self.route),
        ):
            rng=Recorder([0])
            with self.subTest(rows=rows,route=route):
                with self.assertRaises(OriginalSourceUserBirthNameError):
                    consume_original_user_birth_name_pairs(rng,rows,route)
                self.assertEqual(rng.bounds,[])

    def test_unqualified_source_rng_choice_rejected(self):
        rng=Recorder([3,0])
        with self.assertRaises(OriginalSourceUserBirthNameError):
            consume_original_user_birth_name_pairs(rng,self.players,self.route)
        self.assertEqual(rng.bounds,[3,3])


if __name__=="__main__":
    unittest.main()
