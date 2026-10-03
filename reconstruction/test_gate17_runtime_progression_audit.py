"""Tests for the read-only Gate-17 runtime progression audit."""
from dataclasses import dataclass
import unittest

from gate17_country_allocation_scope import (
    PlayableCountryAllocationPlan,
    PlayableCountryAllocationScope,
)
from gate17_runtime_progression_audit import (
    Gate17RuntimeProgressionAuditError,
    audit_runtime_playable_progression,
)


@dataclass(frozen=True)
class Allocation:
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


def plan_fixture():
    return PlayableCountryAllocationPlan(
        catalog_sha256="e" * 64,
        countries=(
            PlayableCountryAllocationScope(
                country_id=26,
                country_name="England",
                selectable_league_ids=(0, 2),
                allocation_ids=(0, 1),
                ranking_endpoint_ids=(0, 2, 11),
            ),
            PlayableCountryAllocationScope(
                country_id=66,
                country_name="Scotland",
                selectable_league_ids=(27, 28),
                allocation_ids=(7,),
                ranking_endpoint_ids=(27, 28),
            ),
        ),
        assigned_allocation_ids=(0, 1, 7),
        ignored_allocation_ids=(),
    )


def records_fixture():
    return (
        Allocation(7, 27, 9, 8, 28, 0, 1),
        Allocation(0, 0, 18, 19, 2, 0, 1),
        Allocation(1, 0, 17, 17, 11, 0, 0),
    )


def memberships_fixture():
    memberships = {}
    for club_id in range(100, 120):
        memberships[club_id] = 0
    for club_id in range(200, 224):
        memberships[club_id] = 2
    for club_id in range(270, 280):
        memberships[club_id] = 27
    for club_id in range(280, 290):
        memberships[club_id] = 28
    return memberships


def rankings_fixture():
    return {
        0: tuple(range(100, 120)),
        2: tuple(range(200, 224)),
        11: (205,),
        27: tuple(range(270, 280)),
        28: tuple(range(280, 290)),
    }


class FakeState:
    def __init__(self, rankings=None):
        self.league_allocation_records = records_fixture()
        self.club_competition_membership = memberships_fixture()
        self.rankings = rankings_fixture() if rankings is None else rankings
        self.calls = []

    def season_transition_ranking(self, competition_id):
        self.calls.append(competition_id)
        return self.rankings.get(competition_id)


class Gate17RuntimeProgressionAuditTests(unittest.TestCase):
    def test_complete_runtime_state_previews_without_mutating_memberships(self):
        state = FakeState()
        before = dict(state.club_competition_membership)

        audit = audit_runtime_playable_progression(plan_fixture(), state)

        self.assertTrue(audit.complete)
        self.assertTrue(audit.ranking_capability.complete)
        self.assertIsNotNone(audit.allocation_preview)
        self.assertTrue(audit.runtime_memberships_unchanged)
        self.assertEqual(
            state.calls,
            [0, 2, 11, 27, 28],
        )
        self.assertEqual(state.club_competition_membership, before)
        self.assertEqual(audit.required_endpoint_ids, (0, 2, 11, 27, 28))
        self.assertEqual(
            audit.allocation_preview.assigned_allocation_ids,
            (7, 0, 1),
        )
        self.assertEqual(
            tuple(exchange.allocation_id for exchange in audit.allocation_preview.exchanges),
            (7, 7, 0, 0, 1),
        )
        self.assertTrue(audit.as_dict()["complete"])

    def test_missing_runtime_ranking_stops_before_exchange_preview(self):
        rankings = rankings_fixture()
        rankings[28] = None
        state = FakeState(rankings)
        before = dict(state.club_competition_membership)

        audit = audit_runtime_playable_progression(plan_fixture(), state)

        self.assertFalse(audit.complete)
        self.assertFalse(audit.ranking_capability.complete)
        self.assertEqual(audit.ranking_capability.unresolved_endpoint_ids, (28,))
        self.assertIsNone(audit.allocation_preview)
        self.assertEqual(state.club_competition_membership, before)

    def test_ranking_resolver_must_not_mutate_membership_state(self):
        state = FakeState()

        def mutating_resolver(competition_id):
            state.calls.append(competition_id)
            if competition_id == 2:
                state.club_competition_membership[100] = 999
            return state.rankings[competition_id]

        state.season_transition_ranking = mutating_resolver

        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "ranking resolution mutated",
        ):
            audit_runtime_playable_progression(plan_fixture(), state)

    def test_runtime_ranking_payload_must_be_tuple_or_none(self):
        state = FakeState()
        state.rankings[2] = [200, 201]

        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "immutable tuple or None",
        ):
            audit_runtime_playable_progression(plan_fixture(), state)

    def test_missing_runtime_surface_and_bad_membership_container_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "lacks allocation records",
        ):
            audit_runtime_playable_progression(plan_fixture(), object())

        state = FakeState()
        state.club_competition_membership = tuple(state.club_competition_membership.items())
        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "must be a dict",
        ):
            audit_runtime_playable_progression(plan_fixture(), state)

    def test_runtime_membership_identities_must_be_exact_non_negative_ints(self):
        for memberships, message in (
            ({True: 0}, "club IDs"),
            ({1: True}, "competition IDs"),
            ({-1: 0}, "club IDs"),
            ({1: -1}, "competition IDs"),
        ):
            state = FakeState()
            state.club_competition_membership = memberships
            with self.subTest(memberships=memberships):
                with self.assertRaisesRegex(
                    Gate17RuntimeProgressionAuditError,
                    message,
                ):
                    audit_runtime_playable_progression(plan_fixture(), state)

    def test_lower_level_plan_drift_is_wrapped_in_runtime_contract(self):
        plan = plan_fixture()
        bad = PlayableCountryAllocationPlan(
            catalog_sha256=plan.catalog_sha256,
            countries=(
                PlayableCountryAllocationScope(
                    country_id=26,
                    country_name="England",
                    selectable_league_ids=(0, 2),
                    allocation_ids=(0,),
                    ranking_endpoint_ids=(0, 2, 11),
                ),
            ),
            assigned_allocation_ids=(0, 1),
            ignored_allocation_ids=(),
        )
        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "runtime ranking capability audit failed",
        ):
            audit_runtime_playable_progression(bad, FakeState())

    def test_invalid_plan_endpoint_identity_fails_closed(self):
        plan = plan_fixture()
        bad = PlayableCountryAllocationPlan(
            catalog_sha256=plan.catalog_sha256,
            countries=(
                PlayableCountryAllocationScope(
                    country_id=26,
                    country_name="England",
                    selectable_league_ids=(0,),
                    allocation_ids=(0,),
                    ranking_endpoint_ids=(True,),
                ),
            ),
            assigned_allocation_ids=(0,),
            ignored_allocation_ids=(),
        )
        with self.assertRaisesRegex(
            Gate17RuntimeProgressionAuditError,
            "invalid ranking endpoint ID",
        ):
            audit_runtime_playable_progression(bad, FakeState())


if __name__ == "__main__":
    unittest.main()
