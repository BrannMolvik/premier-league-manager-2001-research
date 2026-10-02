from __future__ import annotations

from datetime import date
from types import SimpleNamespace
import struct
import unittest

from fm2001_data import (
    COUNTRY_RECORD_SIZE,
    COUNTRY_TABLE_OFFSET,
    FM2001Database,
)
from game_state import GameCalendar, GameState


def source_country(country_id: int, boundaries):
    return SimpleNamespace(
        id=int(country_id),
        transfer_window_boundaries=tuple(
            (int(week), int(weekday))
            for week, weekday in boundaries
        ),
    )


class CountryTransferWindowSourceTests(unittest.TestCase):
    def test_static_country_bytes_28_through_35_are_parsed_as_four_pairs(self):
        data = bytearray(COUNTRY_TABLE_OFFSET + 4 + COUNTRY_RECORD_SIZE)
        struct.pack_into("<I", data, COUNTRY_TABLE_OFFSET, 1)
        row = COUNTRY_TABLE_OFFSET + 4
        struct.pack_into("<I", data, row, 26)
        data[row + 28:row + 36] = bytes((48, 4, 39, 5, 0, 0, 0, 0))

        database = object.__new__(FM2001Database)
        database.static = bytes(data)
        database.countries = []
        database.english = SimpleNamespace(get=lambda _index: "England")

        database._parse_countries()

        self.assertEqual(
            database.countries[0].transfer_window_boundaries,
            ((48, 4), (39, 5), (0, 0), (0, 0)),
        )


class CountryTransferWindowRuntimeTests(unittest.TestCase):
    def test_england_closes_march_30_and_reopens_may_31_2001(self):
        england = source_country(
            26,
            ((48, 4), (39, 5), (0, 0), (0, 0)),
        )
        state = GameState(
            calendar=GameCalendar(date(2001, 3, 29)),
            players={},
            countries={26: england},
            country_transfer_window_open={26: True},
        )

        self.assertEqual(state.advance_one_day(), date(2001, 3, 30))
        self.assertFalse(state.country_transfer_window_open[26])

        state.calendar.current_date = date(2001, 5, 30)
        self.assertEqual(state.advance_one_day(), date(2001, 5, 31))
        self.assertTrue(state.country_transfer_window_open[26])

    def test_four_boundaries_toggle_in_calendar_order(self):
        spain = source_country(
            73,
            ((48, 4), (13, 5), (22, 1), (30, 7)),
        )
        state = GameState(
            calendar=GameCalendar(date(2000, 7, 3)),
            players={},
            countries={73: spain},
            country_transfer_window_open={73: True},
        )

        expected = (
            (date(2000, 9, 29), False),
            (date(2000, 11, 27), True),
            (date(2001, 1, 28), False),
            (date(2001, 5, 31), True),
        )
        for on_date, open_state in expected:
            state.calendar.current_date = on_date
            self.assertEqual(state.run_country_transfer_window_day(), (73,))
            self.assertEqual(
                state.country_transfer_window_open[73],
                open_state,
            )

    def test_disabled_zero_weekday_pair_does_not_toggle(self):
        country = source_country(
            26,
            ((48, 4), (39, 5), (0, 0), (1, 0)),
        )
        state = GameState(
            calendar=GameCalendar(date(2000, 7, 3)),
            players={},
            countries={26: country},
            country_transfer_window_open={26: True},
        )

        self.assertEqual(state.run_country_transfer_window_day(), ())
        self.assertTrue(state.country_transfer_window_open[26])


if __name__ == "__main__":
    unittest.main()
