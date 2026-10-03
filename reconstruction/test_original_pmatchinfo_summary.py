import unittest
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path

from complete_fixture_report import assemble_complete_fixture_report
from original_fixture_report_capture import NativeCapturedScalar
from original_pmatchinfo_summary import (
    ordinary_pmatchinfo_summary_lines, summary_line_pixels,
    ordinary_pmatchinfo_pitch_pixels,
    ordinary_pmatchinfo_possession_lines, load_pmatchinfo_nested_font,
)
from original_pmenu_chrome import validate_original_pmenu_font
from test_complete_fixture_report import contract


def complete_report():
    fixture = SimpleNamespace(id=2, home_club_id=5, away_club_id=11)
    metadata, statistics, result = contract(fixture)
    fields = {0x30: 123456, 0x98: 1, 0x9A: 2}
    copies = tuple(NativeCapturedScalar(s.report_offset, s.calculator_offset,
        fields[s.report_offset].to_bytes(len(s.value), 'little'))
        if s.report_offset in fields else s for s in metadata.scalar_copies)
    metadata = replace(metadata, scalar_copies=copies)
    return assemble_complete_fixture_report(2, result, metadata, statistics, 0)


class PMatchInfoSummaryTests(unittest.TestCase):
    def setUp(self):
        self.report = complete_report()
        self.players = {0: SimpleNamespace(first_name='First', surname='Player'),
                        1: SimpleNamespace(first_name='Émile', surname='Unused'),
                        2: SimpleNamespace(first_name='Unused', surname='Referee')}

    def test_actual_report_fields_and_two_referee_identities(self):
        lines = ordinary_pmatchinfo_summary_lines(self.report, self.players)
        self.assertEqual([line.text for line in lines],
                         ['Attendance 123,456  Explicit synthetic contract  ', 'Ref. É Referee', 'Mom: First Player'])
        self.assertEqual([line.rect for line in lines],
                         [(172, 50, 416, 16), (380, 68, 208, 16), (172, 68, 208, 16)])

    def test_partial_and_secondary_contexts_stay_closed(self):
        self.assertEqual(ordinary_pmatchinfo_summary_lines(SimpleNamespace(), self.players), ())
        report = replace(self.report, metadata=replace(self.report.metadata, previous_scores=(0, 0)))
        self.assertEqual(ordinary_pmatchinfo_summary_lines(report, self.players), ())

    def test_absent_mom_does_not_invent_name(self):
        report = replace(self.report, selected_player_id=-1)
        self.assertEqual(len(ordinary_pmatchinfo_summary_lines(report, self.players)), 2)

    def test_unrepresentable_or_missing_names_are_not_replaced(self):
        self.players[1].first_name = '无法'
        lines = ordinary_pmatchinfo_summary_lines(self.report, self.players)
        self.assertEqual([line.setup_call_va for line in lines], [0x485091, 0x485101])
        self.assertEqual(len(ordinary_pmatchinfo_summary_lines(self.report, {})), 1)

    def test_original_font_native_center_and_sixteen_pixel_clip(self):
        font = validate_original_pmenu_font(Path(__file__).resolve().parents[1] / 'original_assets/source')
        line = ordinary_pmatchinfo_summary_lines(self.report, self.players)[0]
        x, y, width, height, png = summary_line_pixels(line, font)
        self.assertEqual(x, max(172, 172 + 416 // 2 - font.measure_text(line.text) // 2))
        self.assertEqual(y, 50)  # Native line origin is 49, clipped at the control top.
        self.assertLessEqual(height, 16)
        self.assertLessEqual(width, 416)
        self.assertTrue(png.startswith(b'\x89PNG'))

    def test_source_attendance_buffer_retains_caption_and_native_small_value_branch(self):
        for value, rendered in ((0, '55,241'), (1, '55,241'), (2, '0,002'), (1000, '1,000')):
            copies = tuple(replace(s, value=value.to_bytes(4, 'little')) if s.report_offset == 0x30
                           else s for s in self.report.metadata.scalar_copies)
            report = replace(self.report, metadata=replace(self.report.metadata, scalar_copies=copies))
            line = ordinary_pmatchinfo_summary_lines(report, self.players)[0]
            self.assertEqual(line.text, f'Attendance {rendered}  Explicit synthetic contract  ')
            self.assertEqual(int.from_bytes(report.metadata.scalar_copies[0].value, 'little'), value)

    def test_default_nested_pitch_uses_source_owner_and_two_row_crop(self):
        from original_pmatchinfo_presenter import OriginalPMatchInfoArtPlacement
        from gate13_original_pixel_preview import encode_rgba_png
        rgba = b''.join(bytes((row, 0, 0, 255)) * 294 for row in range(78))
        pitch = OriginalPMatchInfoArtPlacement('pitch_normal', (233, -2, 294, 78), (294, 78), rgba)
        snapshot = SimpleNamespace(selected_tab_event_id=1, art=(pitch,))
        pixels = ordinary_pmatchinfo_pitch_pixels(self.report, snapshot)
        self.assertEqual(pixels[:4], (233, 145, 294, 76))
        self.assertEqual(pixels[4], encode_rgba_png(294, 76, rgba[2 * 294 * 4:]))
        snapshot.selected_tab_event_id = 2
        self.assertIsNone(ordinary_pmatchinfo_pitch_pixels(self.report, snapshot))
        snapshot.selected_tab_event_id = 1
        self.assertIsNone(ordinary_pmatchinfo_pitch_pixels(None, snapshot))

    def test_possession_columns_consume_captured_bytes_in_reverse_source_order(self):
        report = replace(self.report, possession=replace(self.report.possession, averages=bytes((12, 43, 91))))
        snapshot = SimpleNamespace(selected_tab_event_id=1)
        lines = ordinary_pmatchinfo_possession_lines(report, snapshot)
        self.assertEqual([line.text for line in lines], ['91%', '43%', '12%'])
        self.assertEqual([line.rect for line in lines], [(295,187,30,20), (370,187,30,20), (443,187,30,20)])
        font = load_pmatchinfo_nested_font(Path(__file__).resolve().parents[1] / 'original_assets/source')
        for line in lines:
            pixels = summary_line_pixels(line, font)
            self.assertLessEqual(pixels[3], 20)
            self.assertGreaterEqual(pixels[1], 187)
        snapshot.selected_tab_event_id = 2
        self.assertEqual(ordinary_pmatchinfo_possession_lines(report, snapshot), ())
        snapshot.selected_tab_event_id = 1
        self.assertEqual(ordinary_pmatchinfo_possession_lines(None, snapshot), ())
