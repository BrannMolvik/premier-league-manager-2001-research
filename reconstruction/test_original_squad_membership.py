import unittest

from original_squad_membership import (
    NativeSquadMember, prepare_ordered_squad_membership, native_squad_slot,
)


def member(player_id, selection, role, preferred=None):
    return NativeSquadMember(player_id, selection, role, role if preferred is None else preferred)


class NativeSquadMembershipTests(unittest.TestCase):
    def test_three_original_ordering_phases_are_not_one_role_sort(self):
        supplied = (
            member(0, 2, 8), member(1, 0, 3), member(2, 4, 10),
            member(3, 1, 1), member(4, 4, 4), member(5, 0, 9),
            member(6, 3, 6), member(7, 2, 2), member(8, 1, 0),
        )
        result = prepare_ordered_squad_membership(supplied, substitute_quota=3)
        self.assertEqual(tuple(m.player_id for m in result.members), (4, 2, 6, 5, 1, 7, 0, 8, 3))
        self.assertEqual(result.first_list_boundary, 16)
        self.assertEqual(result.cleared_player_ids, ())
        self.assertEqual(supplied[0].player_id, 0)  # No live roster mutation.

    def test_equal_roles_keep_original_order_in_every_group(self):
        supplied = tuple(member(i, selection, 4) for i, selection in
                         enumerate((1, 4, 0, 3, 2, 4, 0, 1, 2, 3)))
        result = prepare_ordered_squad_membership(supplied, substitute_quota=3)
        self.assertEqual(tuple(m.player_id for m in result.members), (1, 5, 3, 9, 2, 6, 4, 8, 0, 7))

    def test_earliest_excess_selection_is_cleared_and_preferred_role_restored(self):
        supplied = tuple(member(i, 4, 10, 2) for i in range(12))
        supplied += tuple(member(i, 3, 10, 7) for i in range(12, 16))
        supplied += tuple(member(i, 2, 10, 1) for i in range(16, 29))
        supplied += tuple(member(i, 1, 10, 3) for i in range(29, 34))
        result = prepare_ordered_squad_membership(supplied, substitute_quota=3)
        self.assertEqual(result.cleared_player_ids, (0, 12, 16, 17, 29, 30))
        by_id = {m.player_id: m for m in result.members}
        for player_id in result.cleared_player_ids:
            self.assertEqual(by_id[player_id].selection, 0)
            self.assertEqual(by_id[player_id].current_role, by_id[player_id].preferred_role)
        self.assertEqual(result.first_list_boundary, 20)

    def test_completed_first_and_reserve_slots_do_not_split_first_twenty(self):
        supplied = tuple(member(i, 4 if i < 11 else 3 if i < 16 else 2 if i < 27 else 1, i % 20)
                         for i in range(30))
        result = prepare_ordered_squad_membership(supplied, substitute_quota=5)
        first = tuple(native_squad_slot(result, visible_index=i, reserve=False, source_count=30)
                      for i in range(20))
        reserve = tuple(native_squad_slot(result, visible_index=i, reserve=True, source_count=30)
                        for i in range(20))
        self.assertEqual(first, tuple(range(16)) + (-1,) * 4)
        self.assertEqual(reserve, tuple(range(16, 30)) + (-1,) * 6)

    def test_missing_first_xi_and_bench_slots_remain_native_empty_rows(self):
        supplied = tuple(member(i, selection, i) for i, selection in
                         enumerate((4, 4, 3, 0, 0, 2, 1)))
        result = prepare_ordered_squad_membership(supplied, substitute_quota=3)
        slots = tuple(native_squad_slot(result, visible_index=i, reserve=False, source_count=7)
                      for i in range(20))
        self.assertEqual(slots, (0, 1) + (-1,) * 9 + (2, -1, -1, 3, 4) + (-1,) * 4)

    def test_unknown_or_fabricated_inputs_are_not_defaulted(self):
        with self.assertRaises(ValueError):
            prepare_ordered_squad_membership((member(1, 0, 1),), substitute_quota=None)
        with self.assertRaises(ValueError):
            prepare_ordered_squad_membership((member(1, 0, 1),) * 2, substitute_quota=3)
        with self.assertRaises(ValueError):
            prepare_ordered_squad_membership(tuple(member(i, 0, 1) for i in range(41)), substitute_quota=3)
        result = prepare_ordered_squad_membership((member(1, 0, 1),), substitute_quota=3)
        with self.assertRaises(ValueError):
            native_squad_slot(result, visible_index=0, reserve=True, source_count=20)
        with self.assertRaises(ValueError):
            native_squad_slot(None, visible_index=0, reserve=True, source_count=1)


if __name__ == '__main__':
    unittest.main()
