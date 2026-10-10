import unittest

from original_squad_membership import NativeSquadMember, prepare_ordered_squad_membership
from original_squad_paired_presenter import build_paired_squad_snapshot
import test_original_squad_presenter as fixtures


class PairedSquadTests(unittest.TestCase):
    def test_real_host_draws_number_in_both_owners_and_keeps_empty_slots_blank(self):
        from types import SimpleNamespace
        from dataclasses import asdict
        from original_game_host import OriginalGameTkHost
        from original_squad_resources import squad_view_transition
        from original_squad_row_style import build_paired_roster_text_overlays
        from test_original_game_host import (
            FakeRoot, FakeTk, presenter, fake_squad_row_text_resources,
        )
        rows = tuple(SimpleNamespace(**(asdict(row) | {'club_relative_assignment': i}))
                     for i, row in enumerate(self.rows(30)))
        members = tuple(NativeSquadMember(row.player_id,
            4 if i < 11 else 3 if i < 16 else 2 if i < 27 else 1,
            i % 20, i % 20) for i, row in enumerate(rows))
        paired = build_paired_squad_snapshot(
            prepare_ordered_squad_membership(members, substitute_quota=5), rows)
        resources = fake_squad_row_text_resources()
        numbers = [o for o in build_paired_roster_text_overlays(paired, resources)
                   if o.x < 60 or 419 <= o.x < 441]
        self.assertEqual(len(numbers), 30)
        self.assertEqual({o.text for o in numbers}, {str(i) for i in range(30)})
        first = [o for o in numbers if o.x < 60]
        reserve = [o for o in numbers if o.x >= 419]
        self.assertEqual((len(first), len(reserve)), (16, 14))
        for o in numbers:
            left = 38 if o.x < 60 else 419
            self.assertGreaterEqual(o.x, left)
            self.assertLessEqual(o.x + o.width, left + 22)
            self.assertEqual(o.source_rgb, (255, 255, 255))
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk,
            squad_row_text_resources=resources)
        host.canvas.delete('all')
        frame = SimpleNamespace(presentation=SimpleNamespace(panel_class='PSquadScreen',
            squad_view_transition=squad_view_transition(3), squad=paired.first,
            paired_squad=paired))
        self.assertEqual(host._draw_squad_rows(frame), 8 + 6 * 30)

    def test_host_renders_both_source_owners_without_dropping_players(self):
        from types import SimpleNamespace
        from original_game_host import OriginalGameTkHost
        from original_squad_resources import squad_view_transition
        from test_original_game_host import (
            FakeRoot, FakeTk, presenter, fake_squad_row_text_resources,
        )
        rows = self.rows(30)
        members = tuple(NativeSquadMember(row.player_id,
            4 if i < 11 else 3 if i < 16 else 2 if i < 27 else 1,
            i % 20, i % 20) for i, row in enumerate(rows))
        paired = build_paired_squad_snapshot(
            prepare_ordered_squad_membership(members, substitute_quota=5), rows)
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk,
            squad_row_text_resources=fake_squad_row_text_resources())
        host.canvas.delete('all')
        frame = SimpleNamespace(presentation=SimpleNamespace(panel_class='PSquadScreen',
            squad_view_transition=squad_view_transition(3), squad=paired.first,
            paired_squad=paired))
        count = host._draw_squad_rows(frame)
        self.assertEqual(count, 4 * 2 + 5 * 30)
        self.assertEqual(len(host.canvas.images), count)
        # The reserve source-font name starts at the recovered +381 offset.
        self.assertTrue(any(image[:2] == (113 + 381, 234) for image in host.canvas.images))

    def test_paired_text_uses_exact_shared_child_transform_and_pixels(self):
        from pathlib import Path
        from original_squad_row_style import (
            load_verified_squad_row_text_resources, build_paired_roster_text_overlays,
            build_first_roster_column_heading_overlays,
            build_first_roster_role_overlays, build_first_roster_name_overlays,
            build_first_roster_scf_numeric_overlays,
        )
        rows = self.rows(30)
        members = tuple(NativeSquadMember(row.player_id,
            4 if i < 11 else 3 if i < 16 else 2 if i < 27 else 1,
            i % 20, i % 20) for i, row in enumerate(rows))
        membership = prepare_ordered_squad_membership(members, substitute_quota=5)
        paired = build_paired_squad_snapshot(membership, rows)
        resources = load_verified_squad_row_text_resources(
            Path(__file__).resolve().parents[1] / 'original_assets/source')
        def overlays(view):
            return (*build_first_roster_column_heading_overlays(resources),
                    *build_first_roster_role_overlays(view.rows, resources),
                    *build_first_roster_name_overlays(view.rows, resources),
                    *build_first_roster_scf_numeric_overlays(view.rows, resources))
        first, reserve = overlays(paired.first), overlays(paired.reserve)
        actual = build_paired_roster_text_overlays(paired, resources)
        self.assertEqual(actual[:len(first)], first)
        for native, translated in zip(reserve, actual[len(first):]):
            self.assertEqual((translated.x, translated.y), (native.x + 381, native.y))
            self.assertEqual(translated.rgba, native.rgba)
            self.assertEqual(translated.text, native.text)

    def rows(self, count):
        fixture = fixtures.OriginalSquadPresenterTests()
        return tuple(fixture.row(i) for i in range(count))

    def test_complete_native_pair_displays_all_thirty_not_first_twenty(self):
        rows = self.rows(30)
        members = tuple(NativeSquadMember(row.player_id,
            4 if i < 11 else 3 if i < 16 else 2 if i < 27 else 1,
            i % 20, i % 20) for i, row in enumerate(rows))
        membership = prepare_ordered_squad_membership(members, substitute_quota=5)
        snapshot = build_paired_squad_snapshot(membership, rows)
        first = {r.player_id for r in snapshot.first.rows}
        reserve = {r.player_id for r in snapshot.reserve.rows}
        self.assertEqual(len(first), 16)
        self.assertEqual(len(reserve), 14)
        self.assertFalse(first & reserve)
        self.assertEqual(first | reserve, {r.player_id for r in rows})
        self.assertEqual(snapshot.first_empty_slots, (16, 17, 18, 19))
        self.assertEqual(snapshot.reserve_empty_slots, (14, 15, 16, 17, 18, 19))
        self.assertEqual(snapshot.unpresented_player_ids, ())

    def test_empty_first_xi_slots_do_not_move_bench_to_top(self):
        rows = self.rows(7)
        members = tuple(NativeSquadMember(row.player_id, selection, i, i)
            for i, (row, selection) in enumerate(zip(rows, (4, 4, 3, 0, 0, 2, 1))))
        membership = prepare_ordered_squad_membership(members, substitute_quota=3)
        snapshot = build_paired_squad_snapshot(membership, rows)
        self.assertEqual([r.visible_index for r in snapshot.first.rows], [0, 1, 11, 14, 15])
        self.assertEqual(snapshot.first.rows[2].y, 154 + 17 * 11)

    def test_membership_identity_is_mandatory_and_missing_players_are_not_fabricated(self):
        rows = self.rows(3)
        members = tuple(NativeSquadMember(row.player_id, 0, 1, 1) for row in rows)
        membership = prepare_ordered_squad_membership(members, substitute_quota=5)
        for supplied in (rows[:2], (rows[0],) * 3):
            with self.assertRaisesRegex(ValueError, 'do not match'):
                build_paired_squad_snapshot(membership, supplied)
        with self.assertRaisesRegex(ValueError, 'prepared ordered'):
            build_paired_squad_snapshot(None, rows)


if __name__ == '__main__':
    unittest.main()
