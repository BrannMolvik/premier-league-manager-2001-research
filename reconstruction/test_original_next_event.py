"""Ordinary selector/cache lifecycle, distinct from the display projection."""
from dataclasses import replace
from datetime import date, timedelta
import unittest

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_startup import CupClubRefDescriptor
from primary_schedule_shadow import PrimaryScheduleShadowState


class OriginalNextEventTests(unittest.TestCase):
    today = date(2000, 7, 3)

    def node(self, token=0, left=1, right=2, kind='league_match'):
        return StartupScheduleNode(kind, 7, 0, None, 0, 0, 0, 1,
            direct_club_ref(left) if isinstance(left, int) else left,
            direct_club_ref(right) if isinstance(right, int) else right,
            (kind, 7, 0, token))

    def state(self, *buckets):
        return PrimaryScheduleShadowState.from_primary_schedule_buckets(buckets, season_year=2000)

    def lookup(self, state, club=1, resolve=None):
        return state.ordinary_next_candidate(club, self.today,
            resolve or (lambda ref: ref.direct_club_id), lambda entry: False)

    def test_native_direct_status_matrix_and_independent_manager_query(self):
        for flags in range(128):
            for linked in (False, True):
                for club in (1, 2, 3):
                    with self.subTest(flags=flags, linked=linked, club=club):
                        state = self.state((self.node(),))
                        entry = state.days[self.today][0]
                        state.days[self.today] = (replace(entry,
                            payload_filter_bits=flags & 0x61,
                            wrapper_link_state='linked' if linked else 'clear'),)
                        before = state.snapshot()
                        result = self.lookup(state, club)
                        self.assertEqual(result is not None,
                                         not flags & 0x61 and not linked and club in (1, 2))
                        self.assertEqual(state.snapshot(), before)

    def test_bucket_order_current_day_and_actual_calculator_flag_survive_codec(self):
        state = self.state((self.node(8), self.node(3)), (self.node(1),))
        self.assertEqual(self.lookup(state)[1].node_token[-1], 8)
        state.prepare_ordinary_day(self.today, lambda ref: ref.direct_club_id, lambda entry: False)
        state.retain_ordinary_completion(self.today, self.node(8).node_token)
        restored = PrimaryScheduleShadowState.restore(state.snapshot())
        self.assertEqual(self.lookup(restored)[1].node_token[-1], 3)
        self.assertEqual(restored.days[self.today][0].payload_filter_bits, 1)
        with self.assertRaisesRegex(RuntimeError, 'not eligible'):
            restored.retain_ordinary_completion(self.today, self.node(8).node_token)

    def test_unknown_event_constructor_does_not_gain_native_match_defaults(self):
        state = self.state((self.node(kind='unrecovered_event'),))
        entry = state.days[self.today][0]
        self.assertIsNone(entry.payload_filter_bits)
        self.assertIsNone(entry.side_club_cache)
        with self.assertRaisesRegex(RuntimeError, 'flags are unresolved'):
            self.lookup(state)

    def test_second_leg_requires_actual_first_leg_completion_flag(self):
        first = replace(self.node(kind='first_leg_match'), node_token=('cup_first_leg', 7, 11, 0))
        second = replace(self.node(kind='second_leg_match'), node_token=('cup_result', 7, 11, 0))
        state = self.state((first,), (), (), (second,))
        second_date = self.today + timedelta(days=3)
        with self.assertRaisesRegex(RuntimeError, 'unready current-day'):
            state.prepare_ordinary_day(second_date, lambda ref: ref.direct_club_id,
                                       lambda entry: False)
        state.retain_ordinary_completion(self.today, first.node_token)
        state.prepare_ordinary_day(second_date, lambda ref: ref.direct_club_id,
                                   lambda entry: False)

    def test_missing_legacy_fields_remain_unknown(self):
        state = self.state((self.node(),))
        raw = state.snapshot()
        del raw[self.today.isoformat()][0]['payload_filter_bits']
        del raw[self.today.isoformat()][0]['side_club_cache']
        restored = PrimaryScheduleShadowState.restore(raw)
        with self.assertRaisesRegex(RuntimeError, 'flags are unresolved'):
            self.lookup(restored)
        self.assertIsNone(restored.days[self.today][0].side_club_cache)

    def test_uncached_unresolved_reference_does_not_become_candidate_membership(self):
        symbolic = CupClubRefDescriptor(type_code=1, selector=0, reference_token=('source',))
        state = self.state((self.node(left=symbolic, right=4),), (self.node(1),))
        result = self.lookup(state)
        self.assertEqual(result[0], self.today + timedelta(days=1))
        self.assertEqual(state.days[self.today][0].side_club_cache, (None, 4))

    def test_conflict_free_resolution_caches_but_near_peer_requires_postponement(self):
        symbolic = CupClubRefDescriptor(type_code=1, selector=0, reference_token=('source',))
        resolve = lambda ref: ref.direct_club_id if ref.direct_club_id is not None else 1
        state = self.state((self.node(left=symbolic),), (), (), (self.node(1),))
        self.assertEqual(self.lookup(state, resolve=resolve)[0], self.today)
        self.assertEqual(state.days[self.today][0].side_club_cache, (1, 2))
        for buckets in (((self.node(left=symbolic), self.node(1)),),
                        ((self.node(left=symbolic),), (self.node(1),))):
            state = self.state(*buckets)
            with self.assertRaisesRegex(RuntimeError, 'postponement'):
                self.lookup(state, resolve=resolve)

    def test_registration_and_current_day_unready_stay_closed(self):
        symbolic = CupClubRefDescriptor(type_code=1, selector=0, reference_token=('source',))
        state = self.state((self.node(left=symbolic),))
        with self.assertRaisesRegex(RuntimeError, 'registration'):
            state.ordinary_next_candidate(1, self.today, lambda ref: 1, lambda entry: True)
        self.assertEqual(state.days[self.today][0].side_club_cache, (None, 2))
        with self.assertRaisesRegex(RuntimeError, 'postponement'):
            state.prepare_ordinary_day(self.today, lambda ref: ref.direct_club_id,
                                       lambda entry: False)

    def test_corrupt_filter_and_cache_fields_are_rejected(self):
        for field, value in (('payload_filter_bits', True), ('payload_filter_bits', 2),
                             ('side_club_cache', [1, 2]), ('side_club_cache', (2, 1))):
            state = self.state((self.node(),))
            with self.assertRaises(ValueError):
                replace(state.days[self.today][0], **{field: value})

    def test_source_emitted_other_primary_cup_retains_live_owner_and_bucket_order(self):
        from test_human_gameplay import HumanGameplayControllerTests
        controller = HumanGameplayControllerTests().build_controller()
        node = replace(self.node(kind='cup_match'), competition_id=84, round_id=628,
                       extra_time_capable=False, decisive_tiebreak=True, auxiliary_flag=False)
        buckets = ((node,), (), ())
        state = controller.state
        state.install_qualification_cup_primary_schedule(buckets, season_year=2000,
                                                        competition_ids=(84,))
        state.install_primary_matchday_order(buckets, season_year=2000,
                                            qualification_cup_ids=(84,))
        state.install_primary_schedule_shadow(buckets, season_year=2000)
        self.assertEqual(state.qualification_cups.node(node.node_token).competition_id, 84)
        self.assertEqual(state.primary_matchday_order[self.today],
                         (('qualification_cup', node.node_token),))
        self.assertEqual(state.primary_schedule_end_date, self.today + timedelta(days=3))
        self.assertEqual(state.primary_schedule_shadow.days[self.today][0].payload_filter_bits, 0)


if __name__ == '__main__':
    unittest.main()
