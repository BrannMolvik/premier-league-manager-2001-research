import unittest
from types import SimpleNamespace
from dataclasses import replace
from original_pmatchinfo_script_rows import (decoded_report_row_events, ordinary_report_script_rows,
    script_row_text_lines, script_row_pixels, script_row_player_name, script_row_player_color)
from original_fixture_report_packing import pack_native_match_script
from test_original_fixture_report_packing import native_record
from test_complete_fixture_report import contract
from complete_fixture_report import assemble_complete_fixture_report
from original_fixture_report_capture import capture_finalized_native_goals
from native_compact_match import NativeCompactRecord, native_boundary


def chance(minute, *, side=1, outcome=0, inverted=0, participant=2):
    return NativeCompactRecord(minute, 1, ((4, side), (8, participant), (12, 0),
        (0x20, inverted), (0x24, outcome), (0x2C, 0)))


def report_with(records):
    metadata, statistics, result = contract(SimpleNamespace(home_club_id=5, away_club_id=11))
    result.native_compact_events = tuple(records) + (native_boundary(45, 6), native_boundary(90, 7, outcome=0))
    goals = capture_finalized_native_goals(result.native_compact_events)
    result.native_completion_scalars = replace(result.native_completion_scalars,
                                               scores=tuple(len(side) for side in goals))
    return assemble_complete_fixture_report(2, result, metadata, statistics, 0)


class NativeReportRowsTests(unittest.TestCase):
    def test_packed_chance_inverse_widths_not_original_untruncated_fields(self):
        records = tuple(native_record(0x38, {0: 0x123, 0x28: kind, 4: 3,
            8: 34, 12: 33, 0x24: 11, 0x2C: 2}) for kind in range(1, 5))
        decoded = decoded_report_row_events(pack_native_match_script(records))
        self.assertEqual(tuple(e.kind for e in decoded), (1, 2, 3, 4))
        self.assertEqual(tuple(e.minute for e in decoded), (0x23,) * 4)
        self.assertEqual(tuple(decoded[0].field(k) for k in (4, 8, 12, 0x24, 0x2C)),
                         (1, 2, 1, 3, 0))

    def test_every_family_is_consumed_without_manufacturing_opaque_row_fields(self):
        common = {4: 1, 8: 3, 12: 17, 0x10: 9, 0x14: 19,
                  0x18: 1, 0x1C: 0, 0x20: 1, 0x24: 5, 0x2C: 27}
        for command in range(6):
            records = tuple(native_record(0x38, {**common, 0: kind, 0x28: kind,
                           **({8: command} if kind == 11 else {})}) for kind in range(1, 17))
            decoded = decoded_report_row_events(pack_native_match_script(records))
            self.assertEqual(len(decoded), 16)
            self.assertEqual([e.kind for e in decoded],
                [1, 2, 3, 4, 5, None, None, None, 9, 10, None, None, None, None, None, None])

    def test_native_default_list_predicates_and_owner_are_not_score_or_side_inference(self):
        report = report_with((chance(4, side=0), chance(8, outcome=1),
                              chance(12), chance(18, inverted=1)))
        for list_side in (0, 1):
            rows = ordinary_report_script_rows(report, list_side=list_side)
            self.assertEqual([r.event_index for r in rows], [2, 3])
            self.assertEqual([r.participant_side for r in rows], [1, 0])
            self.assertEqual([r.player_id for r in rows], [102, 2])
            self.assertEqual([r.field_74 for r in rows], [0, 1])
            self.assertEqual(rows[0].origin, (39 if list_side else 411, 260))
            self.assertEqual(rows[1].origin[1], 298)

    def test_substitution_duplicates_have_exact_same_pointer_identity_and_side_input(self):
        sub = NativeCompactRecord(30, 10, ((4, 1), (8, 2), (0x2C, 3)))
        report = report_with((sub,))
        for side in (0, 1):
            rows = ordinary_report_script_rows(report, list_side=side)
            self.assertEqual([r.event_index for r in rows], [0, 0])
            self.assertEqual([r.field_78 for r in rows], [0, 1])
            self.assertEqual([r.participant_index for r in rows], [3 if side else 2] * 2)

    def test_six_slots_and_partial_input_remain_closed(self):
        report = report_with(tuple(chance(i) for i in range(1, 10)))
        self.assertEqual(len(ordinary_report_script_rows(report, list_side=1)), 6)
        self.assertEqual(ordinary_report_script_rows(None, list_side=1), ())
        for invalid in (b'', b'\x01\x00', report.script + b'\0'):
            with self.assertRaises(ValueError):
                decoded_report_row_events(invalid)

    def test_written_decimal_suffix_and_substitution_duplicate_number(self):
        sub = NativeCompactRecord(30, 10, ((4, 1), (8, 2), (0x2C, 3)))
        rows = ordinary_report_script_rows(report_with((sub,)), list_side=1)
        self.assertEqual([line.text for line in script_row_text_lines(rows[0])],
                         ['Sub On', '30 MINS'])
        self.assertEqual([line.text for line in script_row_text_lines(rows[1])],
                         ['Sub On', '30'])
        self.assertEqual(script_row_text_lines(rows[0])[0].rect, (249, 262, 185, 12))

    def test_boundary_marker_shifts_the_source_record_and_removes_one_row(self):
        report = report_with((chance(10), native_boundary(20, 9), chance(30)))
        rows = ordinary_report_script_rows(report, list_side=1)
        self.assertEqual([r.event_index for r in rows], [0, 2])
        self.assertEqual([r.event.minute for r in rows], [10, 30])
        # The factory computes duplicate flag BEFORE choosing the next record.
        self.assertEqual([r.field_78 for r in rows], [0, 0])

    def test_repeated_card_producer_marks_the_matching_participant_only(self):
        def card(minute, participant, red):
            return NativeCompactRecord(minute, 5, ((4, 1), (0x14, participant),
                (0x18, 0), (0x1C, red), (0x20, 0)))
        rows = ordinary_report_script_rows(report_with((card(3, 1, 0), card(6, 2, 1),
                                                        card(9, 1, 1))), list_side=1)
        self.assertEqual([r.field_78 for r in rows], [0, 0, 1])

    def test_row_art_and_text_clip_to_native_list_not_label_control_width(self):
        from pathlib import Path
        from original_pmenu_chrome import validate_original_pmenu_font
        images = {name: SimpleNamespace(width=w, height=h, rgba=b'\xff' * (w*h*4))
                  for name, w, h in (('match_name_grid', 185, 36),
                                     ('match_incid_grid', 142, 36), ('score', 14, 14))}
        font = validate_original_pmenu_font(Path(__file__).resolve().parents[1] / 'original_assets/source')
        row = ordinary_report_script_rows(report_with((chance(12),)), list_side=1)[0]
        layers = script_row_pixels(row, images, font)
        self.assertGreater(len(layers), 3)
        self.assertTrue(all(39 <= x and x+w <= 371 and 260 <= y and y+h <= 488
                            for x, y, w, h, png in layers))

    def test_source_abbreviation_and_selection_color_order_fail_closed(self):
        from runtime_state import RuntimePlayer
        row = ordinary_report_script_rows(report_with((chance(12),)), list_side=1)[0]
        player = RuntimePlayer(index=row.player_id, first_name='Paul', surname='Ince',
            club_id=11, nationality_id=29, date_of_birth=None, shirt_number=2,
            height_cm=180, weight_kg=80, positions=(1, 2, 3), current_raw=[0] * 17,
            target_raw=(0,) * 17, development=None)
        players = {player.index: player}
        self.assertIsNone(script_row_player_name(row, players))
        player.match_substitute_available = True
        self.assertEqual(script_row_player_color(row, players), (232, 191, 94))
        self.assertEqual(script_row_player_name(row, players).text, 'P. Ince')
        player.match_active = True
        self.assertEqual(script_row_player_color(row, players), (255, 255, 255))
        player.first_name = '-'
        self.assertEqual(script_row_player_name(row, players).text, 'Ince')
        self.assertIsNone(script_row_player_name(row, {player.index: SimpleNamespace(**vars(player))}))

    def test_shirt_uses_exact_numbered_frame_not_generated_digits(self):
        from pathlib import Path
        from original_pmenu_chrome import validate_original_pmenu_font
        row = ordinary_report_script_rows(report_with((chance(12),)), list_side=1)[0]
        report = report_with((chance(12),))
        frames = b''.join(bytes((i, 0, 0, 255)) * (36 * 32) for i in range(40))
        source = SimpleNamespace(selected_atlas=lambda report, row:
            SimpleNamespace(width=36, height=1280, rgba=frames))
        images = {'_shirt_source': source, 'score': SimpleNamespace(width=14, height=14, rgba=b'\xff' * 784)}
        for name, width in (('match_name_grid', 185), ('match_incid_grid', 142)):
            images[name] = SimpleNamespace(width=width, height=36, rgba=b'\xff' * (width * 36 * 4))
        font = validate_original_pmenu_font(Path(__file__).resolve().parents[1] / 'original_assets/source')
        layers = script_row_pixels(row, images, font, report=report)
        self.assertEqual(layers[2][:4], (39, 262, 36, 32))
        from gate13_original_pixel_preview import encode_rgba_png
        self.assertEqual(layers[2][4], encode_rgba_png(36, 32,
            bytes((row.shirt_number - 1, 0, 0, 255)) * (36 * 32)))
        zero = replace(row, shirt_number=0)
        self.assertFalse(any(layer[:4] == (39, 262, 36, 32)
                             for layer in script_row_pixels(zero, images, font, report=report)))


if __name__ == '__main__':
    unittest.main()
