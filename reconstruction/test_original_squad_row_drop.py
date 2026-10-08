import unittest
from dataclasses import replace

from original_squad_row_drop import drop_original_squad_row
from test_original_squad_preparation import player


class NativeRowDropTests(unittest.TestCase):
    def drop(self, players, source=0, target=1, empty=None, quota=5):
        return drop_original_squad_row(players, source_index=source,
            target_index=target, empty_row_index=empty, substitute_quota=quota)

    def test_populated_swap_preserves_destination_role_aux_and_roster_words(self):
        members = (replace(player(0, 0, 7), current_aux=2),
                   replace(player(1, 4, 4), current_aux=3))
        result = self.drop(members)
        self.assertTrue(result.accepted)
        self.assertEqual([p.player_id for p in result.players], [1, 0])
        target, source = result.players
        self.assertEqual((source.selection, source.current_role, source.current_aux), (4, 4, 3))
        self.assertEqual((target.selection, target.current_role, target.current_aux), (0, 4, 0))
        self.assertEqual(result.first_active_player_ids, (0,))

    def test_xi_to_bench_copies_source_role_to_target_then_resets_source(self):
        members = (replace(player(0, 4, 7), current_aux=2), player(1, 3, 4))
        result = self.drop(members)
        target, source = result.players
        self.assertEqual((target.selection, target.current_role, target.current_aux), (4, 7, 2))
        self.assertEqual((source.selection, source.current_role, source.current_aux), (3, 7, 0))

    def test_reserve_transition_retains_native_role_swap_bytes(self):
        members = (replace(player(0, 2, 7), current_aux=2, reserve_role=3, reserve_aux=1),
                   replace(player(1, 4, 4), current_aux=3))
        target, source = self.drop(members).players
        self.assertEqual((target.selection, target.current_role, target.current_aux), (2, 7, 2))
        self.assertEqual((target.reserve_role, target.reserve_aux), (4, 0))
        self.assertEqual((source.selection, source.current_role, source.current_aux), (4, 4, 3))
        self.assertEqual((source.reserve_role, source.reserve_aux), (7, 2))

    def test_goalkeeper_exception_requires_zero_existing_goalkeepers(self):
        members = (player(0, 0, 1),) + tuple(player(i, 4, 4) for i in range(1, 12))
        result = self.drop(members)
        self.assertEqual((result.players[1].current_role, result.players[1].current_aux), (1, 0))
        members = members[:2] + (player(2, 4, 1),) + members[3:]
        self.assertEqual(self.drop(members).players[1].current_role, 4)

    def test_self_drop_follows_native_clear_and_restore_sequence(self):
        member = replace(player(0, 2, 7), current_aux=2, reserve_role=3, reserve_aux=1)
        actual = self.drop((member,), target=0).players[0]
        self.assertEqual((actual.selection, actual.current_role, actual.current_aux), (2, 7, 2))
        self.assertEqual((actual.reserve_role, actual.reserve_aux), (7, 0))

    def test_empty_first_bench_uses_raw_slot_and_preferred_reset(self):
        member = replace(player(0, 2, 7), preferred_roles=(3, 0, 0), reserve_role=4)
        actual = self.drop((member,), target=11, empty=11).players[0]
        self.assertEqual((actual.selection, actual.current_role, actual.current_aux), (3, 3, 0))
        self.assertEqual(actual.reserve_role, 7)

    def test_empty_xi_preserves_source_role_aux(self):
        member = replace(player(0, 0, 7), current_aux=2)
        self.assertEqual(self.drop((member,), target=0, empty=0).players[0], replace(member, selection=4))

    def test_empty_reserve_requires_original_size_boundary(self):
        members = tuple(player(i, 0, 7) for i in range(30))
        actual = self.drop(members, target=20, empty=0).players[0]
        self.assertEqual(actual.selection, 2)
        self.assertEqual(actual.current_role, 7)
        actual = self.drop(members[:-1], target=20, empty=0).players[0]
        self.assertEqual(actual.selection, 0)

    def test_empty_role_guard_uses_equality_not_greater_equal(self):
        members = (player(0, 0, 7), player(1, 4, 7))
        self.assertFalse(self.drop(members, target=0, empty=0).accepted)
        members += (player(2, 4, 7),)
        self.assertTrue(self.drop(members, target=0, empty=0).accepted)

    def test_native_translated_index_not_pane_label_selects_empty_branch(self):
        members = tuple(player(i, 0, 7) for i in range(30))
        self.assertEqual(self.drop(members, target=19, empty=11).players[0].selection, 3)
        self.assertEqual(self.drop(members, target=20, empty=11).players[0].selection, 1)

    def test_no_synthetic_null_target_or_missing_quota(self):
        for target, empty, quota in ((1, None, 5), (0, 20, 5), (0, None, None)):
            with self.assertRaises(ValueError):
                self.drop((player(0),), target=target, empty=empty, quota=quota)


class NativeRowPointerTests(unittest.TestCase):
    def membership(self):
        from original_squad_membership import NativeSquadMember, prepare_ordered_squad_membership
        return prepare_ordered_squad_membership(tuple(NativeSquadMember(i,
            4 if i < 11 else 3 if i < 13 else 0 if i < 16 else 2 if i < 27 else 1,
            i % 20, i % 20)
            for i in range(30)), substitute_quota=5)

    def test_both_original_parents_map_populated_rows(self):
        from original_squad_pointer import original_squad_row_at_point
        m = self.membership()
        self.assertEqual(original_squad_row_at_point(m, 107, 233, press=True).ordered_index, 0)
        self.assertEqual(original_squad_row_at_point(m, 488, 233, press=True).ordered_index, 16)

    def test_empty_bench_translation_counts_only_preceding_empty_owners(self):
        from original_squad_pointer import original_squad_row_at_point
        m = self.membership()
        hit = original_squad_row_at_point(m, 107, 233 + 13*17)
        self.assertTrue(hit.empty_owner)
        self.assertEqual((hit.visible_index, hit.ordered_index), (13, 13))
        self.assertIsNone(original_squad_row_at_point(m, 107, 233 + 13*17, press=True))
        hit = original_squad_row_at_point(m, 107, 233 + 16*17)
        self.assertEqual(hit.ordered_index, 13)
        self.assertFalse(hit.empty_owner)

    def test_role_column_strict_edges_and_shirt_number_are_not_name_drag(self):
        from original_squad_pointer import original_squad_row_at_point
        m = self.membership()
        for x in (68, 106, 449, 487):
            self.assertIsNone(original_squad_row_at_point(m, x, 233, press=True))
        for x in (67, 107, 448, 488):
            self.assertFalse(original_squad_row_at_point(m, x, 233, press=True).shirt_number)
        for x in (37, 66, 418, 447):
            self.assertTrue(original_squad_row_at_point(m, x, 233, press=True).shirt_number)
        # Dropping a player name in the number/role column still hits its owner.
        self.assertIsNotNone(original_squad_row_at_point(m, 68, 233))

    def test_original_half_open_player_row_not_stats_or_null_lookup(self):
        from original_squad_pointer import original_squad_row_at_point
        m = self.membership()
        for x,y in ((36,233),(263,233),(647,233),(107,232),(107,573)):
            self.assertIsNone(original_squad_row_at_point(m, x, y))
        self.assertIsNotNone(original_squad_row_at_point(m, 107, 249))
        with self.assertRaises(ValueError):
            original_squad_row_at_point(None, 107, 233)


class NativeRowLiveTests(unittest.TestCase):
    def state(self):
        from test_original_squad_preparation import LiveSquadPreparationTests
        return LiveSquadPreparationTests().state()

    def test_live_atomic_drop_and_native_order_refresh(self):
        state = self.state()
        roster = state.ordered_club_roster(1)
        roster[0].set_match_active()
        roster[0].assign_match_position(7, 2)
        roster[1].set_match_substitute_available()
        old = state.original_primary_squad_membership(1, substitute_quota=5)
        target = state.drop_original_primary_squad_row(1, source_index=0,
            target_index=1, substitute_quota=5)
        self.assertIsNotNone(target)
        self.assertTrue(state.players[1].match_active)
        self.assertEqual((state.players[1].current_position, state.players[1].position_aux_code), (7, 2))
        self.assertTrue(state.players[0].match_substitute_available)
        self.assertEqual(state.club_roster_order[1], [m.player_id for m in target.members])
        self.assertEqual(len(state.club_roster_order[1]), len(old.members))

    def test_unqualified_loan_setter_side_effect_fails_without_mutation(self):
        state = self.state()
        state.players[0].loan_listed = True
        before = [(p.match_selection_state_code, p.current_position,
                   p.saved_reserve_role_152) for p in state.ordered_club_roster(1)]
        with self.assertRaisesRegex(RuntimeError, 'loan-list'):
            state.drop_original_primary_squad_row(1, source_index=0,
                target_index=0, empty_row_index=0, substitute_quota=5)
        self.assertEqual(before, [(p.match_selection_state_code, p.current_position,
                   p.saved_reserve_role_152) for p in state.ordered_club_roster(1)])


class NativeHumanSelectionTests(unittest.TestCase):
    def controller(self, bench=5):
        from human_gameplay import HumanGameplayController, HumanManagerState
        from types import SimpleNamespace
        state = NativeRowLiveTests().state()
        state.native_squad_first_formations[1] = 0
        for i,p in enumerate(state.ordered_club_roster(1)):
            if i < 11:
                p.set_match_active()
                # Deliberately not formation-table order: source roles survive.
                p.assign_match_position(1+i, i%4)
            elif i < 11+bench:
                p.set_match_substitute_available()
        c = HumanGameplayController.__new__(HumanGameplayController)
        c.state = state
        c.human = HumanManagerState(club_id=1)
        c.original_squad_membership = state.original_primary_squad_membership(1, substitute_quota=5)
        c._human_selection_competition = lambda: SimpleNamespace(substitute_quota=5, max_non_eu_players=11)
        return c

    def test_native_match_input_is_read_only_and_keeps_actual_roles(self):
        c = self.controller()
        roster = c.state.ordered_club_roster(1)
        before = tuple((p.index,p.match_selection_state_code,p.current_position,p.position_aux_code,
                        p.saved_reserve_role_152,p.saved_reserve_aux_153) for p in roster)
        selection = c.current_selection()
        self.assertEqual([(a.player_index,a.role,a.auxiliary_code) for a in selection.lineup.starters],
                         [(p.index,p.current_position,p.position_aux_code) for p in roster if p.match_active])
        self.assertEqual(selection.participants, tuple(p for p in roster if p.match_active or p.match_substitute_available))
        self.assertEqual(before, tuple((p.index,p.match_selection_state_code,p.current_position,p.position_aux_code,
                        p.saved_reserve_role_152,p.saved_reserve_aux_153) for p in roster))
        self.assertEqual(c.human.starter_ids, tuple(p.index for p in roster if p.match_active))

    def test_partial_native_bench_is_not_autofilled_or_reassigned(self):
        c = self.controller(bench=2)
        with self.assertRaisesRegex(ValueError, 'retained 11 and 2'):
            c.current_selection()
        self.assertEqual(sum(p.match_substitute_available for p in c.state.ordered_club_roster(1)), 2)

    def test_live_drag_updates_owner_and_saved_human_ids(self):
        c = self.controller(bench=2)
        source = next(i for i,m in enumerate(c.original_squad_membership.members) if m.selection == 0)
        self.assertTrue(c.drop_original_squad_row(source, 13, empty_row_index=13))
        self.assertEqual(len(c.human.substitute_ids), 3)
        self.assertEqual(tuple(m.player_id for m in c.original_squad_membership.members),
                         tuple(p.index for p in c.state.ordered_club_roster(1)))


class NativeRowHostTests(unittest.TestCase):
    def host(self):
        from types import SimpleNamespace
        from original_game_host import OriginalGameTkHost
        from front_end_state import FrontEndScreen
        c = NativeHumanSelectionTests().controller(bench=2)
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.presenter = SimpleNamespace(session=SimpleNamespace(gameplay=c,
            navigation=SimpleNamespace(screen=FrontEndScreen.MANAGEMENT)))
        host.management_presenter = SimpleNamespace(squad_view_control_id=3,
            snapshot=lambda: SimpleNamespace(panel_class='PSquadScreen', paired_squad=object()))
        host.active_pmatchinfo_art = None
        host.pmenu_popup_active = False
        host._squad_drag_source = None
        host.draws = 0
        def draw(): host.draws += 1
        host.redraw = draw
        host.error_reporter = self.fail
        return host, c

    def test_host_normal_press_release_fills_original_empty_bench(self):
        from types import SimpleNamespace
        host,c = self.host()
        self.assertTrue(host._press_original_squad_row(SimpleNamespace(x=107,y=233+16*17)))
        source = host._squad_drag_source[1]
        self.assertTrue(host._release_original_squad_row(SimpleNamespace(x=107,y=233+13*17)))
        self.assertIsNone(host._squad_drag_source)
        self.assertEqual(host.draws, 1)
        self.assertTrue(c.state.players[source].match_substitute_available)

    def test_popup_changed_owner_or_outside_release_never_mutates(self):
        from types import SimpleNamespace
        for mode in ('popup','changed','outside'):
            host,c = self.host()
            before = tuple((p.index,p.match_selection_state_code,p.current_position)
                           for p in c.state.ordered_club_roster(1))
            host._press_original_squad_row(SimpleNamespace(x=107,y=233+16*17))
            if mode=='popup': host.pmenu_popup_active=True
            if mode=='changed':
                from dataclasses import replace
                c.original_squad_membership=replace(c.original_squad_membership)
            event = SimpleNamespace(x=-1 if mode=='outside' else 107,y=233+13*17)
            self.assertTrue(host._release_original_squad_row(event))
            self.assertEqual(before, tuple((p.index,p.match_selection_state_code,p.current_position)
                           for p in c.state.ordered_club_roster(1)))
            self.assertEqual(host.draws, 0)

    def test_role_number_and_empty_press_do_not_start_name_drag(self):
        from types import SimpleNamespace
        host,c = self.host()
        self.assertFalse(host._press_original_squad_row(SimpleNamespace(x=80,y=233)))
        self.assertTrue(host._press_original_squad_row(SimpleNamespace(x=40,y=233)))
        self.assertIsNone(host._squad_drag_source)
        self.assertFalse(host._press_original_squad_row(SimpleNamespace(x=107,y=233+13*17)))


class NativeRowSaveTests(unittest.TestCase):
    def test_native_drop_role_flags_order_and_match_inputs_survive_reload(self):
        from internal_save import dumps_human_gameplay, loads_human_gameplay
        from test_internal_save import InternalSaveTests, Database, coefficient_matrix
        c = InternalSaveTests().build_controller()
        c.state.native_squad_first_formations[1] = 0
        c.original_squad_membership = c.state.original_primary_squad_membership(1, substitute_quota=5)
        self.assertTrue(c.drop_original_squad_row(0, 11))
        before = tuple((p.index,p.match_selection_state_code,p.current_position,p.position_aux_code,
                        p.saved_reserve_role_152,p.saved_reserve_aux_153)
                       for p in c.state.ordered_club_roster(1))
        expected = c.current_selection()
        restored = loads_human_gameplay(Database(), coefficient_matrix(), coefficient_matrix(),
                                       dumps_human_gameplay(c))
        self.assertEqual(before, tuple((p.index,p.match_selection_state_code,p.current_position,p.position_aux_code,
                        p.saved_reserve_role_152,p.saved_reserve_aux_153)
                       for p in restored.state.ordered_club_roster(1)))
        actual = restored.current_selection()
        self.assertEqual(actual.lineup, expected.lineup)
        self.assertEqual(tuple(p.index for p in actual.participants),
                         tuple(p.index for p in expected.participants))


if __name__ == '__main__':
    unittest.main()
