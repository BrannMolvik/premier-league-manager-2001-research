from __future__ import annotations

import unittest
from types import SimpleNamespace

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)
from original_league_fixtures_prepared_members import (
    OriginalLeagueFixturesMembersError,
    original_current_league_fixtures_prepared_members,
)
from original_league_fixtures_resources import LEAGUE_FIXTURES_COUNTRY_SELECTORS
from original_league_fixtures_selector_context import (
    build_league_fixtures_selection_context,
)
from procedural_league_state import LiveProceduralLeagueState, ProceduralLeagueFixture


# Firsthand canonical disc metadata (Recovery505): Southport club349 is an
# English (country26) member of Conference7, a real root League kind1 with
# 22 original members. Scottish Premiership27 is NOT Southport's competition.
# The other club names below are deliberately synthetic regression fixtures.
ROOT_ENGLAND = (
    (0, "F.A. Premier League", 9, 1),
    (2, "Division 1 (ENG)", 10, 1),
    (3, "Division 2 (ENG)", 11, 1),
    (4, "Division 3 (ENG)", 12, 1),
    (7, "Conference", 13, 1),
    (89, "Conference 2", 14, 3),
)


def comp(cid, country, ordinal, name, kind=1):
    return SimpleNamespace(
        id=cid,
        country_region_id=country,
        initialization_order_value=ordinal,
        parent_competition_id=None,
        runtime_kind_code=kind,
        name=name,
    )


def source(*, selected_league=7, member_count=22):
    definitions = {cid: comp(cid, 26, order, name, kind)
                   for cid, name, order, kind in ROOT_ENGLAND}
    definitions[27] = comp(27, 66, 7, "Premiership")
    for selector in LEAGUE_FIXTURES_COUNTRY_SELECTORS:
        if selector.country_id in (26, 66):
            continue
        cid = 300 + selector.index
        definitions[cid] = comp(cid, selector.country_id, 1, f"Source {cid}")
    members = (349,) + tuple(range(200, 200 + member_count - 1))
    clubs = {
        cid: SimpleNamespace(
            name="Southport" if cid == 349 else f"Club {cid}",
            short_name="Southport" if cid == 349 else f"Club {cid}",
            country_id=26,
        ) for cid in members
    }
    membership = {cid: selected_league for cid in members}
    fixtures = {
        ("fixture", i): ProceduralLeagueFixture(
            ("fixture", i), members[i], members[(i+1) % len(members)]
        ) for i in range(len(members))
    }
    live = LiveProceduralLeagueState(
        competition_id=selected_league,
        competition_context=0,
        fixtures=fixtures,
        club_ids=members[::-1],  # Deliberately unlike source name order
    )
    state = SimpleNamespace(
        clubs=clubs,
        competitions=definitions,
        club_competition_membership=membership,
        procedural_leagues={(selected_league, 0): live},
        premier_league_table=lambda: (_ for _ in ()).throw(
            AssertionError("Do not substitute Premier League 0")
        ),
    )
    return state


def prepared(state):
    return original_current_league_fixtures_prepared_members(
        human_club_id=349,
        membership=state.club_competition_membership,
        clubs=state.clubs,
        competitions=state.competitions,
        procedural_leagues=state.procedural_leagues,
    )


class OriginalLeagueFixturesPreparedMembersTests(unittest.TestCase):
    def test_verified_original_southport_conference7_is_fifth_league_radio(self):
        state = source()
        context = build_league_fixtures_selection_context(
            club_id=349,
            clubs=state.clubs,
            membership=state.club_competition_membership,
            competitions=state.competitions.values(),
        )
        self.assertEqual(context.active_country_id, 26)
        self.assertEqual(context.selected_competition_id, 7)
        self.assertEqual(context.selected_league_indices[0], 4)
        self.assertEqual(
            tuple((radio.event_id, radio.league_identity)
                  for radio in context.active_league_radios()),
            ((9, 0), (10, 2), (11, 3), (12, 4), (13, 7)),
        )
        self.assertTrue(context.active_league_radios()[-1].selected)

    def test_actual_native_comparator_order_not_first_fixture_encounter(self):
        state = source()
        view = prepared(state)
        self.assertEqual(view.manager_club_id, 349)
        self.assertEqual(view.country_id, 26)
        self.assertEqual(view.competition_id, 7)
        self.assertEqual(len(view.member_club_ids), 22)
        self.assertEqual(view.original_member_comparator_va, 0x4F45E0)
        self.assertEqual(view.original_member_preparation_va, 0x4F4940)
        self.assertEqual(view.member_club_ids[0], 200)
        self.assertEqual(view.member_club_ids[-1], 349)
        self.assertNotEqual(
            view.member_club_ids,
            state.procedural_leagues[(7, 0)].club_ids,
        )
        self.assertEqual(len(state.procedural_leagues[(7, 0)].results), 0)

    def test_current_management_bridge_exposes_only_real_prepared_members(self):
        state = source()
        controller = SimpleNamespace(
            state=state, human=SimpleNamespace(club_id=349)
        )
        bridge = ManagementSourceDataBridge(controller)
        view = bridge.original_nonpl_league_fixtures_prepared_members()
        self.assertEqual(view.competition_id, 7)
        self.assertEqual(len(view.member_club_ids), 22)
        self.assertFalse(hasattr(view, "fixtures_in_source_order"))
        self.assertEqual(len(state.procedural_leagues[(7, 0)].results), 0)

    def test_legacy_scottish_27_token_cannot_reselect_southport_league(self):
        state = source()
        # A global Scottish node or separately displayed Scottish country
        # must not alter the selected manager's original DBRClub League.
        state.procedural_leagues[(27, 0)] = SimpleNamespace(
            competition_id=27, competition_context=0,
        )
        self.assertEqual(prepared(state).competition_id, 7)
        state.club_competition_membership[349] = 27
        with self.assertRaises(OriginalLeagueFixturesMembersError):
            prepared(state)

    def test_membership_and_source_roster_incompleteness_fail_closed(self):
        state = source()
        state.club_competition_membership[215] = 0
        with self.assertRaisesRegex(
            OriginalLeagueFixturesMembersError, "participants disagree"
        ):
            prepared(state)
        state = source()
        state.procedural_leagues.clear()
        with self.assertRaisesRegex(
            OriginalLeagueFixturesMembersError, "context-zero"
        ):
            prepared(state)

    def test_dynamic_current_league_identity_not_hardcoded_to_conference7(self):
        state = source(selected_league=4, member_count=22)
        view = prepared(state)
        self.assertEqual(view.competition_id, 4)
        self.assertEqual(view.country_id, 26)
        self.assertEqual(len(view.member_club_ids), 22)

    def test_unproven_full_key_tie_never_invents_original_qsort_order(self):
        state = source()
        state.clubs[200].short_name = "Same"
        state.clubs[201].short_name = "Same"
        with self.assertRaisesRegex(
            OriginalLeagueFixturesMembersError, "CRT sort tie"
        ):
            prepared(state)

    def test_premier_league_has_separate_native_fixture_source(self):
        state = source()
        state.club_competition_membership[349] = 0
        with self.assertRaisesRegex(
            OriginalLeagueFixturesMembersError, "existing Premier League"
        ):
            prepared(state)

    def test_missing_source_competitions_fail_as_bridge_error(self):
        state = source()
        del state.competitions
        bridge = ManagementSourceDataBridge(SimpleNamespace(
            state=state, human=SimpleNamespace(club_id=349)
        ))
        with self.assertRaisesRegex(
            ManagementPresentationError, "source.*unavailable"
        ):
            bridge.original_nonpl_league_fixtures_prepared_members()


if __name__ == "__main__":
    unittest.main()
