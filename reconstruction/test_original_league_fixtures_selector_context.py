from __future__ import annotations

import unittest
from types import SimpleNamespace

from original_league_fixtures_selector_context import (
    LeagueFixturesSelectorContextError,
    build_league_fixtures_selection_context,
)
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_COUNTRY_SELECTORS,
)


def competition(id, country, order, *, kind=1, name=None, parent=None):
    return SimpleNamespace(
        id=id,
        country_region_id=country,
        parent_competition_id=parent,
        initialization_order_value=order,
        runtime_kind_code=kind,
        name=name or f"Source competition {id}",
    )


def canonical_shaped_definitions():
    definitions = [
        competition(0, 26, 0, name="Premier League"),
        competition(42, 26, 1, name="First Division"),
        competition(900, 26, 2, kind=3, name="Not a League radio"),
        competition(101, 33, 2, name="Second Germany League"),
        competition(100, 33, 1, name="First Germany League"),
        competition(901, 33, 3, kind=2, name="Country Cup"),
        competition(902, 33, 4, parent=100, name="Child not root"),
    ]
    definitions.extend(
        competition(300 + i, selector.country_id, 0)
        for i, selector in enumerate(LEAGUE_FIXTURES_COUNTRY_SELECTORS)
        if selector.country_id not in (26, 33)
    )
    return definitions


def open_context(*, country=26, league=0, definitions=None):
    return build_league_fixtures_selection_context(
        club_id=349,
        clubs={349: SimpleNamespace(country_id=country)},
        membership={349: league},
        competitions=(
            canonical_shaped_definitions() if definitions is None else definitions
        ),
    )


class LeagueFixturesSelectorContextTests(unittest.TestCase):
    def test_manager_current_country_and_original_competition_identity(self):
        context = open_context()
        self.assertEqual(context.active_country_id, 26)
        self.assertEqual(context.selected_competition_id, 0)
        self.assertEqual(context.selected_league_indices, (0,) + (None,) * 7)
        self.assertEqual(
            [(r.event_id, r.league_identity, r.caption, r.selected)
             for r in context.active_league_radios()],
            [(9, 0, "Premier League", True),
             (10, 42, "First Division", False)],
        )

    def test_root_source_order_and_real_league_rtti_candidate_filter(self):
        context = open_context()
        self.assertEqual(
            context.league_candidates[0],
            ((0, "Premier League"), (42, "First Division")),
        )
        self.assertEqual(
            context.league_candidates[1],
            ((100, "First Germany League"), (101, "Second Germany League")),
        )
        self.assertTrue(all(
            option[0] != 900
            for options in context.league_candidates for option in options
        ))

    def test_country_and_league_events_preserve_per_country_index_transactionally(self):
        original = open_context()
        germany = original.accept_native_radio_event(2)
        self.assertEqual(germany.active_country_id, 33)
        self.assertIsNone(germany.selected_competition_id)
        self.assertIsNone(germany.active_league_radios())
        selected = germany.accept_native_radio_event(10)
        self.assertEqual(selected.selected_competition_id, 101)
        england = selected.accept_native_radio_event(1)
        self.assertEqual(england.selected_competition_id, 0)
        again = england.accept_native_radio_event(2)
        self.assertEqual(again.selected_competition_id, 101)
        self.assertEqual(original.active_country_id, 26)
        self.assertEqual(original.selected_league_indices[1], None)

    def test_original_six_radio_limit_and_inactive_radio_do_not_mutate(self):
        context = open_context()
        with self.assertRaisesRegex(LeagueFixturesSelectorContextError, "unconstructed"):
            context.accept_native_radio_event(14)
        self.assertEqual(context.selected_competition_id, 0)
        with self.assertRaises(LeagueFixturesSelectorContextError):
            context.accept_native_radio_event(15)
        with self.assertRaises(LeagueFixturesSelectorContextError):
            context.accept_native_radio_event(True)
        self.assertEqual(context.selected_league_indices[0], 0)

    def test_another_actual_club_competition_is_used_not_unrelated_calendar_event(self):
        context = open_context(country=33, league=101)
        self.assertEqual(context.active_country_id, 33)
        self.assertEqual(context.selected_competition_id, 101)
        # A global LeagueMatch token from any other competition is not an
        # argument to this owner and cannot alter the manager's League.
        self.assertEqual(
            context.accept_native_radio_event(1).active_country_id, 26
        )

    def test_fail_closed_on_missing_or_unqualified_current_manager_identity(self):
        bad = ((999, 0), (26, 999), (26, True), (26, -1))
        for country, league in bad:
            with self.subTest(country=country, league=league):
                with self.assertRaises(LeagueFixturesSelectorContextError):
                    open_context(country=country, league=league)
        with self.assertRaises(LeagueFixturesSelectorContextError):
            build_league_fixtures_selection_context(
                club_id=349, clubs={}, membership={349: 0},
                competitions=canonical_shaped_definitions(),
            )
        with self.assertRaises(LeagueFixturesSelectorContextError):
            build_league_fixtures_selection_context(
                club_id=349,
                clubs={349: SimpleNamespace(country_id=26)},
                membership={},
                competitions=canonical_shaped_definitions(),
            )

    def test_rejects_duplicate_source_identity_and_missing_country_eligibility(self):
        definitions = canonical_shaped_definitions()
        with self.assertRaisesRegex(LeagueFixturesSelectorContextError, "distinct"):
            open_context(definitions=definitions + [definitions[0]])
        without_belgium = [
            item for item in definitions if item.country_region_id != 9
        ]
        with self.assertRaisesRegex(LeagueFixturesSelectorContextError, "six native"):
            open_context(definitions=without_belgium)

    def test_rejects_more_than_six_leagues_no_cup_or_dummy_fallback(self):
        definitions = canonical_shaped_definitions()
        definitions.extend(
            competition(1000 + i, 26, 10 + i) for i in range(5)
        )
        with self.assertRaisesRegex(LeagueFixturesSelectorContextError, "six native"):
            open_context(definitions=definitions)
        only_dummy_for_england = [
            comp for comp in canonical_shaped_definitions()
            if not (comp.country_region_id == 26 and comp.runtime_kind_code == 1)
        ]
        with self.assertRaisesRegex(LeagueFixturesSelectorContextError, "six native"):
            open_context(definitions=only_dummy_for_england)


if __name__ == "__main__":
    unittest.main()
