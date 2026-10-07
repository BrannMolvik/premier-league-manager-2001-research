"""Regression coverage for source-backed PPreMatch dynamic text binding."""
from datetime import date
from types import SimpleNamespace
import unittest

from gate14_fastview_surfaced_picture_selection import (
    build_fastview_surfaced_resource_selection,
)
from gate14_prematch_text_binding import (
    PREMATCH_DATE_FORMATTER_VA,
    PREMATCH_DATE_MONTH_NAME_HELPER_VA,
    PREMATCH_DATE_MONTH_TABLE_VA,
    PREMATCH_DATE_SUFFIX_TABLE_VA,
    PREMATCH_MONTH_NAMES,
    PREMATCH_ORDINAL_SUFFIXES,
    PREMATCH_REFRESH_VA,
    PREMATCH_STADIUM_DISPLAY_GETTER_VA,
    PREMATCH_STADIUM_NA_LITERALS,
    PREMATCH_STADIUM_SHORT_NAME_FALLBACK_OFFSET,
    PREMATCH_TEAM_DISPLAY_NAME_GETTER_VA,
    PREMATCH_TEAM_DISPLAY_RUNTIME_OVERRIDE_HELPER_VA,
    PREMATCH_TEAM_SHORT_NAME_RUNTIME_OFFSET,
    PrematchTextBindingError,
    build_prematch_dynamic_text,
    format_prematch_source_date,
    prematch_text_binding_contract,
    source_prematch_stadium_display_name,
    source_prematch_team_display_name,
)


def club(
    country_id,
    basename,
    fan_base_index,
    *,
    short_name,
    stadium,
):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
        short_name=short_name,
        stadium=stadium,
    )


class PrematchTextBindingTests(unittest.TestCase):
    def setUp(self):
        self.clubs = {
            10: club(
                26,
                "arsenal",
                25,
                short_name="Arsenal",
                stadium="Highbury",
            ),
            11: club(
                26,
                "chelsea",
                14,
                short_name="Chelsea",
                stadium="Stamford Bridge",
            ),
            12: club(
                31,
                "psg",
                8,
                short_name="Paris SG",
                stadium="Parc des Princes",
            ),
        }
        self.countries = {
            26: SimpleNamespace(graphics_directory="England"),
            31: SimpleNamespace(graphics_directory="France"),
        }

    def _selection(self, *, match_date=date(2001, 1, 13), override=None):
        return build_fastview_surfaced_resource_selection(
            match_date=match_date,
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=override,
        )

    def test_exact_source_addresses_and_language_tables_are_retained(self):
        self.assertEqual(PREMATCH_REFRESH_VA, 0x49A610)
        self.assertEqual(PREMATCH_TEAM_DISPLAY_NAME_GETTER_VA, 0x40DA70)
        self.assertEqual(PREMATCH_TEAM_DISPLAY_RUNTIME_OVERRIDE_HELPER_VA, 0x403600)
        self.assertEqual(PREMATCH_TEAM_SHORT_NAME_RUNTIME_OFFSET, 0x0C)
        self.assertEqual(PREMATCH_STADIUM_DISPLAY_GETTER_VA, 0x514270)
        self.assertEqual(PREMATCH_STADIUM_NA_LITERALS, ("N/A", "NA"))
        self.assertEqual(PREMATCH_STADIUM_SHORT_NAME_FALLBACK_OFFSET, 0x0C)
        self.assertEqual(PREMATCH_DATE_FORMATTER_VA, 0x64D150)
        self.assertEqual(PREMATCH_DATE_MONTH_NAME_HELPER_VA, 0x64D140)
        self.assertEqual(PREMATCH_DATE_SUFFIX_TABLE_VA, 0x84A024)
        self.assertEqual(PREMATCH_DATE_MONTH_TABLE_VA, 0x84A030)
        self.assertEqual(PREMATCH_ORDINAL_SUFFIXES, ("th", "st", "nd", "rd"))
        self.assertEqual(
            PREMATCH_MONTH_NAMES,
            (
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ),
        )

    def test_native_ordinal_suffix_and_full_month_date_format(self):
        expected = {
            date(2001, 1, 1): "1st January 2001",
            date(2001, 2, 2): "2nd February 2001",
            date(2001, 3, 3): "3rd March 2001",
            date(2001, 4, 4): "4th April 2001",
            date(2001, 5, 11): "11th May 2001",
            date(2001, 6, 12): "12th June 2001",
            date(2001, 7, 13): "13th July 2001",
            date(2001, 8, 21): "21st August 2001",
            date(2001, 9, 22): "22nd September 2001",
            date(2001, 10, 23): "23rd October 2001",
            date(2001, 12, 31): "31st December 2001",
        }
        for source_date, text in expected.items():
            with self.subTest(source_date=source_date):
                self.assertEqual(format_prematch_source_date(source_date), text)

    def test_league_match_binds_exact_visible_dynamic_text(self):
        bound = build_prematch_dynamic_text(
            self._selection(),
            clubs=self.clubs,
            competition_name="F.A. Premier League",
            weather_code=2,
            temperature_c=-3,
            home_team_name_override=None,
            away_team_name_override=None,
        )
        self.assertEqual(
            bound.fixture_header,
            "F.A. Premier League MATCH TODAY AT Highbury",
        )
        self.assertEqual(
            bound.date_weather,
            "13th January 2001 Raining -3°C",
        )
        self.assertEqual(bound.home_team_identity, "Arsenal")
        self.assertEqual(bound.versus, "V")
        self.assertEqual(bound.away_team_identity, "Chelsea")
        self.assertEqual(bound.stadium_display_name, "Highbury")
        self.assertEqual(bound.competition_display_name, "F.A. Premier League")
        self.assertEqual(bound.weather_label, "Raining")
        self.assertTrue(bound.source_state_bound)
        self.assertFalse(bound.text_pixels_rasterized)
        self.assertFalse(bound.complete_prematch_frame)
        self.assertFalse(bound.gate14_complete)

    def test_explicit_match_background_override_drives_same_stadium_helper(self):
        bound = build_prematch_dynamic_text(
            self._selection(override=12),
            clubs=self.clubs,
            competition_name="UEFA Cup",
            weather_code=0,
            temperature_c=16,
            home_team_name_override=None,
            away_team_name_override=None,
        )
        self.assertEqual(
            bound.fixture_header,
            "UEFA Cup MATCH TODAY AT Parc des Princes",
        )
        self.assertEqual(bound.stadium_display_name, "Parc des Princes")

    def test_stadium_na_literals_fall_back_exactly_to_short_name(self):
        for literal in PREMATCH_STADIUM_NA_LITERALS:
            source = SimpleNamespace(stadium=literal, short_name="Fallback Club")
            with self.subTest(literal=literal):
                self.assertEqual(
                    source_prematch_stadium_display_name(source),
                    "Fallback Club",
                )

    def test_team_identity_requires_explicit_override_or_short_name_fallback(self):
        source = SimpleNamespace(short_name="Arsenal")
        self.assertEqual(
            source_prematch_team_display_name(source, runtime_override=None),
            "Arsenal",
        )
        self.assertEqual(
            source_prematch_team_display_name(
                source,
                runtime_override="Network Arsenal",
            ),
            "Network Arsenal",
        )
        with self.assertRaisesRegex(PrematchTextBindingError, "override"):
            source_prematch_team_display_name(source, runtime_override="")

    def test_friendly_branch_uses_exact_localized_fallback(self):
        bound = build_prematch_dynamic_text(
            self._selection(match_date=date(2001, 6, 2)),
            clubs=self.clubs,
            competition_name=None,
            weather_code=1,
            temperature_c=20,
            home_team_name_override=None,
            away_team_name_override=None,
        )
        self.assertEqual(
            bound.fixture_header,
            "Friendly MATCH TODAY AT Highbury",
        )
        self.assertEqual(
            bound.date_weather,
            "2nd June 2001 Sunny 20°C",
        )

    def test_invalid_supplied_state_fails_closed(self):
        selection = self._selection()
        with self.assertRaisesRegex(PrematchTextBindingError, "weather code"):
            build_prematch_dynamic_text(
                selection,
                clubs=self.clubs,
                competition_name="F.A. Premier League",
                weather_code=5,
                temperature_c=10,
                home_team_name_override=None,
                away_team_name_override=None,
            )
        with self.assertRaisesRegex(PrematchTextBindingError, "signed byte"):
            build_prematch_dynamic_text(
                selection,
                clubs=self.clubs,
                competition_name="F.A. Premier League",
                weather_code=0,
                temperature_c=128,
                home_team_name_override=None,
                away_team_name_override=None,
            )
        with self.assertRaisesRegex(PrematchTextBindingError, "competition"):
            build_prematch_dynamic_text(
                selection,
                clubs=self.clubs,
                competition_name="",
                weather_code=0,
                temperature_c=10,
                home_team_name_override=None,
                away_team_name_override=None,
            )

    def test_contract_keeps_raster_and_frame_completion_false(self):
        contract = prematch_text_binding_contract()
        self.assertTrue(contract["dynamic_text_state_binding_available"])
        self.assertEqual(contract["stadium_na_literals"], ("N/A", "NA"))
        self.assertEqual(contract["ordinal_suffixes"], ("th", "st", "nd", "rd"))
        self.assertFalse(contract["text_pixels_rasterized"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
