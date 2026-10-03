import unittest
from dataclasses import replace

from native_compact_match import (
    NativeCompactRecord, finalize_native_compact_events, native_boundary,
    native_full_time_outcome,
)
from original_fixture_report_packing import pack_live_native_match_script, pack_native_match_script
from original_fixture_report_capture import capture_finalized_native_goals, NativeCapturedGoal


def chance(minute, outcome=0, kind=1, identity=0):
    return NativeCompactRecord(minute, kind, ((4, 0), (8, identity), (12, 1),
                                            (0x20, 0), (0x24, outcome), (0x2C, 1)))


def complete(*records):
    return tuple(records) + (native_boundary(45, 6), native_boundary(90, 7, outcome=2))


def finalize(records, spacing=0, cutoff=0):
    return finalize_native_compact_events(records, spacing=spacing, cutoff=cutoff)


class NativeCompactFinalizerTests(unittest.TestCase):
    def test_last_exact_miss_pruned_first_and_input_unchanged(self):
        source = complete(*(chance(i + 1, 1, identity=i) for i in range(10)))
        result = finalize(source)
        self.assertEqual([r.field(8) for r in result if r.kind == 1], list(range(8)))
        self.assertEqual(len(source), 12)

    def test_presentation_miss_only_pruned_above_twelve(self):
        result = finalize(complete(*(chance(i + 1, 4, identity=i) for i in range(14))))
        self.assertEqual([r.field(8) for r in result if r.kind == 1], list(range(12)))

    def test_no_forced_truncation_of_goals_penalties_or_protected_minutes(self):
        for source in (complete(*(chance(i + 1, 3) for i in range(15))),
                       complete(*(chance(i + 1, 1, kind=4) for i in range(15))),
                       complete(*(chance(0, 1) for _ in range(15))),
                       complete(*(chance(130, 1) for _ in range(15)))):
            self.assertEqual(len(finalize(source)), len(source))
        source = complete(*(chance(i + 1, 1) for i in range(15)))
        self.assertEqual(len(finalize(source, cutoff=15)), len(source))

    def test_pruning_count_stops_at_penalties_but_script_does_not(self):
        source = (native_boundary(45, 6), native_boundary(90, 9),
                  *(chance(130, 1) for _ in range(15)), native_boundary(130, 7, outcome=0))
        self.assertEqual(len(finalize(source)), len(source))
        self.assertTrue(pack_live_native_match_script(finalize(source)))

    def test_spacing_looks_past_boundaries_and_couples_incident_substitution(self):
        incident = NativeCompactRecord(42, 5, ((4, 0), (0x10, 2), (0x20, 1)))
        substitution = NativeCompactRecord(42, 10, ((4, 0), (8, 2), (0x2C, 11)))
        source = (chance(44), native_boundary(45, 6), incident, substitution,
                  chance(47), native_boundary(90, 7, outcome=1))
        result = finalize(source, spacing=3)
        self.assertEqual([(r.minute, r.kind) for r in result],
                         [(44, 1), (45, 6), (47, 5), (47, 10), (50, 1), (90, 7)])

    def test_spacing_skips_penalties_boundary_in_lookahead(self):
        source = (native_boundary(45, 6), chance(89), native_boundary(90, 9),
                  chance(88), native_boundary(130, 7, outcome=0))
        result = finalize(source, spacing=3)
        self.assertEqual([r.minute for r in result if r.kind == 1], [89, 92])

    def test_unsigned_spacing_compare_and_signed_stable_sort(self):
        source = complete(chance(0x7FFFFFFF), chance(2))
        result = finalize(source, spacing=1)
        self.assertEqual(result[0].minute, -0x80000000)
        self.assertEqual(result[-1].minute, 0x7FFFFFFF)

    def test_zero_next_minute_and_cutoff_protect_spacing(self):
        result = finalize(complete(chance(20), chance(0)), spacing=3)
        self.assertEqual([r.minute for r in result if r.kind == 1], [0, 20])
        result = finalize(complete(chance(20), chance(1)), spacing=3, cutoff=20)
        self.assertEqual([r.minute for r in result if r.kind == 1], [1, 20])

    def test_boundary_clamps_immediate_predecessor_only(self):
        result = finalize((native_boundary(45, 6), chance(97), chance(96),
                           native_boundary(90, 7, outcome=0)))
        self.assertEqual([r.minute for r in result if r.kind == 1], [90, 97])

    def test_prior_extra_time_boundary_stops_all_later_corrections(self):
        source = (native_boundary(45, 6), native_boundary(90, 8),
                  native_boundary(105, 8), chance(140), native_boundary(120, 7, outcome=2))
        self.assertEqual([r.minute for r in finalize(source) if r.kind == 1], [140])

    def test_stable_ties_keep_original_link_order(self):
        source = complete(chance(30, identity=2), chance(10, identity=1), chance(30, identity=3))
        result = finalize(source, cutoff=130)
        self.assertEqual([r.field(8) for r in result if r.kind == 1], [1, 2, 3])

    def test_boundary_payload_and_malformed_input_fail_closed(self):
        for records in ((), (native_boundary(45, 6),),
                        (NativeCompactRecord(90, 7), native_boundary(45, 6)),
                        [native_boundary(45, 6), native_boundary(90, 7, outcome=2)]):
            with self.assertRaises(ValueError):
                finalize(records)
        with self.assertRaises(ValueError):
            native_boundary(90, 7)
        with self.assertRaises(ValueError):
            native_boundary(45, 6, outcome=0)
        with self.assertRaises(ValueError):
            NativeCompactRecord(1, 1, ((4, 0), (4, 1)))

    def test_live_fields_encode_identically_without_allocating_fake_snapshots(self):
        source = complete(chance(11, 5))
        snapshots = []
        for record in source:
            snapshot = bytearray(0x38)
            for offset, value in ((0, record.minute), (0x28, record.kind)) + record.fields:
                snapshot[offset:offset + 4] = value.to_bytes(4, 'little')
            snapshots.append(bytes(snapshot))
        self.assertEqual(pack_live_native_match_script(source),
                         pack_native_match_script(tuple(snapshots)))
        incomplete = replace(source[0], fields=tuple(p for p in source[0].fields if p[0] != 12))
        with self.assertRaisesRegex(ValueError, 'Missing source-written'):
            pack_live_native_match_script((incomplete,))

    def test_full_time_uses_explicit_aggregate_away_goal_and_penalty_inputs(self):
        self.assertEqual(native_full_time_outcome((1, 0), (-1, -1), (0, 0)), 0)
        self.assertEqual(native_full_time_outcome((0, 1), (-1, -1), (0, 0)), 1)
        self.assertEqual(native_full_time_outcome((1, 1), (-1, -1), (0, 0)), 2)
        self.assertEqual(native_full_time_outcome((1, 2), (2, 1), (9, 0)), 0)
        self.assertEqual(native_full_time_outcome((0, 2), (3, 1), (0, 9)), 0)
        self.assertEqual(native_full_time_outcome((2, 1), (1, 2), (0, 9)), 1)
        self.assertEqual(native_full_time_outcome((1, 1), (-1, -1), (4, 3)), 0)
        self.assertEqual(native_full_time_outcome((1, 1), (-1, -1), (3, 4)), 1)
        with self.assertRaises(ValueError):
            native_full_time_outcome((1, 1), None, (0, 0))

    def test_goal_capture_uses_finalized_native_side_and_low_byte_fields(self):
        from match_events import ChanceRecord, ChanceSource
        from native_compact_match import compact_record_from_live_event
        own = ChanceRecord(ChanceSource.OPEN_PLAY, 3, 1, 7, side_inversion=True,
                           secondary_player_side=0, secondary_player_index=4)
        record = compact_record_from_live_event(20, own)
        self.assertEqual(record.field(4), 0)
        goals = capture_finalized_native_goals(finalize(complete(record, chance(10, 1))))
        self.assertEqual(goals, ((NativeCapturedGoal(7, 20, 1),), ()))
        later = (native_boundary(45, 6), native_boundary(90, 9), chance(130),
                 native_boundary(130, 7, outcome=0))
        self.assertEqual(capture_finalized_native_goals(finalize(later)), ((), ()))

    def test_live_participant_statistics_pack_without_padding_or_snapshot_defaults(self):
        from match_postmatch import FinalizedParticipantStatistics
        from original_fixture_report_packing import pack_live_participant_statistics, pack_native_participant_statistics
        records = tuple(FinalizedParticipantStatistics(i, 4 + i % 7, b'\x01\x00' * 4)
                        for i in range(18))
        native = []
        for record in records:
            raw = bytearray(0x4C)
            raw[0x30] = record.rating
            raw[0x35:0x3D] = record.skill_flags
            native.append(bytes(raw))
        actual = pack_live_participant_statistics(records)
        self.assertEqual(actual, pack_native_participant_statistics(tuple(native)))
        self.assertEqual(len(actual), 27)
        for invalid in ((), list(records), records[::-1]):
            with self.assertRaises(ValueError):
                pack_live_participant_statistics(invalid)

    def test_report_player_selection_preserves_native_order_history_tie_and_zero_sentinel(self):
        from match_postmatch import FinalizedParticipantStatistics as Stats
        from match_postmatch import FinalizedSideParticipantStatistics as Side
        from match_postmatch import select_native_report_player_id
        def side(ids, ratings):
            return Side(ids, tuple(Stats(i, r, bytes(8)) for i, r in enumerate(ratings)))
        sides = (side((5, 6), (7, 8)), side((8, 9), (8, 8)))
        self.assertEqual(select_native_report_player_id(sides, ((10, 7), (7, 7))), 6)
        self.assertEqual(select_native_report_player_id(sides, ((10, 7), (9, 8))), 8)
        zeros = (side((5,), (0,)), side((6,), (0,)))
        self.assertEqual(select_native_report_player_id(zeros, ((9,), (10,))), -1)
        with self.assertRaises(ValueError):
            select_native_report_player_id(sides, ((1,), (2,)))


if __name__ == '__main__':
    unittest.main()
