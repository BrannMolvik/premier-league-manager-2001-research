"""Tests for Gate-17 LeagueAllocation ranking endpoint readiness."""
from dataclasses import dataclass
import unittest

from gate17_allocation_ranking_capability import (
    Gate17AllocationRankingCapabilityError,
    audit_allocation_ranking_capability,
    audit_allocation_ranking_resolver,
)
from gate17_country_allocation_scope import (
    PlayableCountryAllocationPlan,
    PlayableCountryAllocationScope,
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
        catalog_sha256="a" * 64,
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
        ignored_allocation_ids=(99,),
    )


def records_fixture():
    return (
        Allocation(0, 0, 18, 19, 2, 0, 1),
        Allocation(1, 0, 17, 17, 11, 0, 0),
        Allocation(7, 27, 9, 8, 28, 0, 1),
        Allocation(99, 500, 0, 0, 501, 0, 0),
    )


class Gate17AllocationRankingCapabilityTests(unittest.TestCase):
    def test_complete_rankings_cover_every_exact_source_position(self):
        audit = audit_allocation_ranking_capability(
            plan_fixture(),
            records_fixture(),
            {
                0: tuple(range(100, 120)),
                2: tuple(range(200, 224)),
                11: (205,),
                27: tuple(range(270, 280)),
                28: tuple(range(280, 290)),
            },
        )

        self.assertTrue(audit.complete)
        self.assertEqual(audit.assigned_allocation_ids, (0, 1, 7))
        self.assertEqual(audit.resolved_allocation_ids, (0, 1, 7))
        self.assertEqual(audit.unresolved_allocation_ids, ())
        self.assertEqual(audit.required_endpoint_ids, (0, 2, 11, 27, 28))
        self.assertEqual(audit.resolved_endpoint_ids, (0, 2, 11, 27, 28))
        self.assertEqual(audit.unresolved_endpoint_ids, ())
        self.assertEqual(audit.entries[0].endpoint_a.required_positions, (18, 19))
        self.assertEqual(audit.entries[2].endpoint_a.required_positions, (9, 8))
        self.assertEqual(audit.as_dict()["complete"], True)

    def test_missing_endpoint_is_reported_without_mutation_or_policy_guess(self):
        audit = audit_allocation_ranking_capability(
            plan_fixture(),
            records_fixture(),
            {
                0: tuple(range(100, 120)),
                2: tuple(range(200, 224)),
                11: (205,),
                27: tuple(range(270, 280)),
                28: None,
            },
        )

        self.assertFalse(audit.complete)
        self.assertEqual(audit.resolved_allocation_ids, (0, 1))
        self.assertEqual(audit.unresolved_allocation_ids, (7,))
        self.assertEqual(audit.resolved_endpoint_ids, (0, 2, 11, 27))
        self.assertEqual(audit.unresolved_endpoint_ids, (28,))
        endpoint = audit.entries[2].endpoint_b
        self.assertFalse(endpoint.resolved)
        self.assertEqual(endpoint.ranking_length, None)
        self.assertEqual(endpoint.failure_reason, "ranking endpoint is unavailable")

    def test_short_ranking_fails_exact_required_position(self):
        audit = audit_allocation_ranking_capability(
            plan_fixture(),
            records_fixture(),
            {
                0: tuple(range(100, 19 + 100)),
                2: tuple(range(200, 224)),
                11: (205,),
                27: tuple(range(270, 280)),
                28: tuple(range(280, 290)),
            },
        )
        self.assertFalse(audit.complete)
        self.assertEqual(audit.unresolved_allocation_ids, (0,))
        self.assertEqual(audit.unresolved_endpoint_ids, (0,))
        endpoint = audit.entries[0].endpoint_a
        self.assertEqual(endpoint.required_positions, (18, 19))
        self.assertEqual(endpoint.ranking_length, 19)
        self.assertIn("required position 19", endpoint.failure_reason)

    def test_negative_source_position_stays_explicitly_unresolved(self):
        rows = list(records_fixture())
        rows[0] = Allocation(0, 0, -1, 0, 2, 0, 1)
        audit = audit_allocation_ranking_capability(
            plan_fixture(),
            tuple(rows),
            {
                0: tuple(range(100, 120)),
                2: tuple(range(200, 224)),
                11: (205,),
                27: tuple(range(270, 280)),
                28: tuple(range(280, 290)),
            },
        )
        self.assertFalse(audit.entries[0].endpoint_a.resolved)
        self.assertIn("negative ranking position", audit.entries[0].endpoint_a.failure_reason)

    def test_resolver_is_called_once_per_required_endpoint_in_plan_order(self):
        calls = []
        rankings = {
            0: tuple(range(100, 120)),
            2: tuple(range(200, 224)),
            11: (205,),
            27: tuple(range(270, 280)),
            28: tuple(range(280, 290)),
        }

        def resolver(competition_id):
            calls.append(competition_id)
            return rankings[competition_id]

        audit = audit_allocation_ranking_resolver(
            plan_fixture(),
            records_fixture(),
            resolver,
        )
        self.assertTrue(audit.complete)
        self.assertEqual(calls, [0, 2, 11, 27, 28])

    def test_plan_record_drift_fails_closed(self):
        plan = plan_fixture()
        with self.assertRaisesRegex(
            Gate17AllocationRankingCapabilityError,
            "missing rows",
        ):
            audit_allocation_ranking_capability(
                plan,
                records_fixture()[1:],
                {},
            )

        bad_plan = PlayableCountryAllocationPlan(
            catalog_sha256=plan.catalog_sha256,
            countries=(
                PlayableCountryAllocationScope(
                    country_id=26,
                    country_name="England",
                    selectable_league_ids=(0, 2),
                    allocation_ids=(0,),
                    ranking_endpoint_ids=(0, 2),
                ),
            ),
            assigned_allocation_ids=(0, 1),
            ignored_allocation_ids=(),
        )
        with self.assertRaisesRegex(
            Gate17AllocationRankingCapabilityError,
            "assignment mismatch",
        ):
            audit_allocation_ranking_capability(
                bad_plan,
                records_fixture(),
                {},
            )

    def test_invalid_rankings_fail_closed(self):
        for rankings, message in (
            ({0: [1, 2]}, "immutable tuple"),
            ({0: (1, 1)}, "duplicate club ID"),
            ({-1: (1,)}, "non-negative integers"),
            ({0: (True,)}, "invalid club ID"),
        ):
            with self.subTest(rankings=rankings):
                with self.assertRaisesRegex(
                    Gate17AllocationRankingCapabilityError,
                    message,
                ):
                    audit_allocation_ranking_capability(
                        plan_fixture(),
                        records_fixture(),
                        rankings,
                    )


if __name__ == "__main__":
    unittest.main()
