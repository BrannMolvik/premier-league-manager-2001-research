"""Tests for full TeamSelect-playable LeagueAllocation previews."""
from dataclasses import dataclass
import unittest

from gate17_country_allocation_scope import (
    PlayableCountryAllocationPlan,
    PlayableCountryAllocationScope,
)
from gate17_playable_allocation_preview import (
    Gate17PlayableAllocationPreviewError,
    preview_playable_allocation_exchanges,
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
        catalog_sha256="b" * 64,
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


def rankings_fixture():
    return {
        0: tuple(range(100, 120)),
        2: tuple(range(200, 224)),
        11: (205,),
        27: tuple(range(270, 280)),
        28: tuple(range(280, 290)),
    }


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


class Gate17PlayableAllocationPreviewTests(unittest.TestCase):
    def test_previews_all_assigned_rows_in_source_order_without_mutating_input(self):
        memberships = memberships_fixture()
        before = dict(memberships)

        preview = preview_playable_allocation_exchanges(
            plan_fixture(),
            records_fixture(),
            rankings_fixture(),
            memberships,
        )

        self.assertEqual(memberships, before)
        self.assertTrue(preview.ranking_capability.complete)
        self.assertEqual(preview.assigned_allocation_ids, (0, 1, 7))
        self.assertEqual(
            tuple(exchange.allocation_id for exchange in preview.exchanges),
            (0, 0, 1, 7, 7),
        )
        self.assertEqual(len(preview.exchanges), 5)

        self.assertEqual(preview.memberships_after[118], 2)
        self.assertEqual(preview.memberships_after[119], 2)
        self.assertEqual(preview.memberships_after[200], 0)
        self.assertEqual(preview.memberships_after[201], 0)
        self.assertEqual(preview.memberships_after[117], 2)
        self.assertEqual(preview.memberships_after[205], 0)

        self.assertEqual(preview.memberships_after[279], 28)
        self.assertEqual(preview.memberships_after[278], 28)
        self.assertEqual(preview.memberships_after[280], 27)
        self.assertEqual(preview.memberships_after[281], 27)

        self.assertEqual(
            set(preview.changed_club_ids),
            {117, 118, 119, 200, 201, 205, 278, 279, 280, 281},
        )
        self.assertEqual(
            tuple(summary.country_id for summary in preview.country_summaries),
            (26, 66),
        )
        self.assertEqual(preview.country_summaries[0].exchange_count, 3)
        self.assertEqual(preview.country_summaries[1].exchange_count, 2)
        self.assertEqual(preview.catalog_sha256, "b" * 64)

        payload = preview.as_dict()
        self.assertEqual(payload["exchange_count"], 5)
        self.assertTrue(payload["ranking_capability"]["complete"])
        self.assertEqual(payload["assigned_allocation_ids"], [0, 1, 7])

    def test_incomplete_ranking_capability_blocks_before_any_exchange(self):
        memberships = memberships_fixture()
        before = dict(memberships)
        rankings = rankings_fixture()
        rankings[28] = None

        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "rankings are incomplete",
        ):
            preview_playable_allocation_exchanges(
                plan_fixture(),
                records_fixture(),
                rankings,
                memberships,
            )
        self.assertEqual(memberships, before)

    def test_missing_membership_is_reported_through_source_executor(self):
        memberships = memberships_fixture()
        memberships.pop(280)

        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "club without live competition membership",
        ):
            preview_playable_allocation_exchanges(
                plan_fixture(),
                records_fixture(),
                rankings_fixture(),
                memberships,
            )

    def test_missing_row_and_source_order_drift_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "missing rows",
        ):
            preview_playable_allocation_exchanges(
                plan_fixture(),
                records_fixture()[1:],
                rankings_fixture(),
                memberships_fixture(),
            )

        rows = list(records_fixture())
        rows[0], rows[1] = rows[1], rows[0]
        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "do not preserve source row order",
        ):
            preview_playable_allocation_exchanges(
                plan_fixture(),
                tuple(rows),
                rankings_fixture(),
                memberships_fixture(),
            )

    def test_duplicate_rows_and_bad_membership_payloads_fail_closed(self):
        rows = records_fixture()
        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "duplicate LeagueAllocation record ID",
        ):
            preview_playable_allocation_exchanges(
                plan_fixture(),
                rows + (rows[0],),
                rankings_fixture(),
                memberships_fixture(),
            )

        for memberships, message in (
            ([(1, 0)], "must be a mapping"),
            ({-1: 0}, "club IDs"),
            ({1: -1}, "competition IDs"),
            ({True: 0}, "club IDs"),
        ):
            with self.subTest(memberships=memberships):
                with self.assertRaisesRegex(
                    Gate17PlayableAllocationPreviewError,
                    message,
                ):
                    preview_playable_allocation_exchanges(
                        plan_fixture(),
                        records_fixture(),
                        rankings_fixture(),
                        memberships,
                    )

    def test_country_assignment_drift_fails_closed(self):
        plan = plan_fixture()
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

        with self.assertRaisesRegex(
            Gate17PlayableAllocationPreviewError,
            "country assignment does not match",
        ):
            preview_playable_allocation_exchanges(
                bad_plan,
                records_fixture(),
                rankings_fixture(),
                memberships_fixture(),
            )


if __name__ == "__main__":
    unittest.main()
