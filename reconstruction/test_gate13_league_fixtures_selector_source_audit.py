"""Tests for the fail-closed PLeagueFixtures selector source-data audit."""
from types import SimpleNamespace
import unittest

from gate13_league_fixtures_selector_source_audit import (
    LeagueFixturesSelectorSourceAuditError,
    audit_league_fixtures_selector_source,
)


COUNTRIES = (26, 33, 40, 73, 66, 31, 24, 9)


def controller(*, country_id=26, competition_id=0):
    state = SimpleNamespace(
        clubs={
            12: SimpleNamespace(
                index=12,
                country_id=country_id,
                competition_id=competition_id,
            )
        },
        club_competition_membership={12: competition_id},
        # Deliberately present in a misleading order. The audit must never use
        # this mapping to manufacture the native DBRCountry array order.
        competitions={
            999: SimpleNamespace(id=999, name="Wrong"),
            competition_id: SimpleNamespace(
                id=competition_id,
                name="Current",
            ),
        },
    )
    return SimpleNamespace(
        state=state,
        human=SimpleNamespace(club_id=12),
    )


def complete_source():
    return {
        26: ((0, "Premier"), (14, "First")),
        33: ((101, "Bundesliga"),),
        40: ((102, "Serie A"),),
        73: ((103, "Primera"),),
        66: ((104, "Scottish Premier"),),
        31: ((105, "Division 1"),),
        24: ((106, "Eredivisie"),),
        9: ((107, "First Division"),),
    }


class LeagueFixturesSelectorSourceAuditTests(unittest.TestCase):
    def test_current_runtime_stays_blocked_without_native_country_arrays(self):
        result = audit_league_fixtures_selector_source(controller())

        self.assertEqual(result.country_selector_ids, COUNTRIES)
        self.assertEqual(result.country_selector_events, tuple(range(1, 9)))
        self.assertEqual(result.current_country_id, 26)
        self.assertEqual(result.current_country_selector_index, 0)
        self.assertEqual(result.current_competition_id, 0)
        self.assertEqual(result.source_array_offset, 0x48)
        self.assertEqual(result.source_count_offset, 0x4C)
        self.assertEqual(result.supplied_country_ids, ())
        self.assertEqual(result.missing_country_ids, COUNTRIES)
        self.assertFalse(result.dynamic_league_order_available)
        self.assertFalse(result.ready_for_integrated_selector_state)
        self.assertEqual(
            result.blocker_codes,
            ("dbrcountry_competition_array_order_unmaterialized",),
        )

    def test_complete_explicit_native_order_resolves_current_selector(self):
        result = audit_league_fixtures_selector_source(
            controller(),
            source_cast_leagues_by_country=complete_source(),
        )

        self.assertEqual(result.supplied_country_ids, COUNTRIES)
        self.assertEqual(result.missing_country_ids, ())
        self.assertEqual(result.current_country_league_ids, (0, 14))
        self.assertEqual(
            result.current_country_league_captions,
            ("Premier", "First"),
        )
        self.assertEqual(result.current_country_selected_league_index, 0)
        self.assertEqual(result.current_country_league_events, (9, 10))
        self.assertTrue(result.dynamic_league_order_available)
        self.assertTrue(result.ready_for_integrated_selector_state)
        self.assertEqual(result.blocker_codes, ())

    def test_partial_explicit_source_remains_fail_closed(self):
        source = complete_source()
        del source[9]
        result = audit_league_fixtures_selector_source(
            controller(),
            source_cast_leagues_by_country=source,
        )

        self.assertEqual(result.missing_country_ids, (9,))
        self.assertEqual(result.current_country_selected_league_index, 0)
        self.assertFalse(result.dynamic_league_order_available)
        self.assertFalse(result.ready_for_integrated_selector_state)
        self.assertEqual(
            result.blocker_codes,
            ("dbrcountry_competition_array_order_incomplete",),
        )

    def test_current_competition_must_exist_in_exact_current_country_order(self):
        source = complete_source()
        source[26] = ((14, "First"),)
        with self.assertRaisesRegex(
            LeagueFixturesSelectorSourceAuditError,
            "current league is absent",
        ):
            audit_league_fixtures_selector_source(
                controller(),
                source_cast_leagues_by_country=source,
            )

    def test_invalid_explicit_source_is_rejected_not_reordered(self):
        cases = (
            {**complete_source(), 999: ((1, "Extra"),)},
            {**complete_source(), 26: ((0, "Premier"), (0, "Duplicate"))},
            {**complete_source(), 26: tuple((i, f"L{i}") for i in range(7))},
        )
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(LeagueFixturesSelectorSourceAuditError):
                    audit_league_fixtures_selector_source(
                        controller(),
                        source_cast_leagues_by_country=value,
                    )

    def test_active_human_source_identity_is_required(self):
        for value in (
            SimpleNamespace(state=controller().state, human=None),
            SimpleNamespace(
                state=SimpleNamespace(
                    clubs={},
                    club_competition_membership={},
                ),
                human=SimpleNamespace(club_id=12),
            ),
        ):
            with self.subTest(value=value):
                with self.assertRaises(LeagueFixturesSelectorSourceAuditError):
                    audit_league_fixtures_selector_source(value)


if __name__ == "__main__":
    unittest.main()
