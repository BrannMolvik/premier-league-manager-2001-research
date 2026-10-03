"""Tests for the fail-closed Gate-17 full-scope preflight."""
from dataclasses import replace
import unittest

from gate17_allocation_ranking_capability import (
    AllocationEndpointRequirement,
    AllocationRankingCapabilityAudit,
    AllocationRankingCapabilityEntry,
)
from gate17_full_scope_preflight import (
    Gate17FullScopePreflightError,
    build_full_scope_preflight,
)
from gate17_human_scope_capability import (
    HumanScopeCapabilityAudit,
    HumanScopeCapabilityEntry,
)
from gate17_playable_allocation_preview import (
    PlayableAllocationPreview,
    PlayableCountryExchangeSummary,
)
from league_transition import LeagueMembershipExchange


CATALOG = "c" * 64


def human_audit(*, complete=True):
    supported = (1, 2) if complete else (1,)
    unsupported = () if complete else (2,)
    entry = HumanScopeCapabilityEntry(
        scope_id="26:0",
        country_id=26,
        country_name="England",
        competition_id=0,
        competition_name="Premier",
        selectable_club_ids=(1, 2),
        supported_club_ids=supported,
        unsupported_club_ids=unsupported,
        fully_supported=complete,
    )
    return HumanScopeCapabilityAudit(
        catalog_sha256=CATALOG,
        backend_selectable_club_ids=supported,
        catalog_selectable_club_ids=(1, 2),
        backend_club_ids_outside_catalog=(),
        entries=(entry,),
    )


def endpoint(competition_id, *, resolved=True):
    return AllocationEndpointRequirement(
        competition_id=competition_id,
        required_positions=(0,),
        ranking_length=1 if resolved else None,
        resolved=resolved,
        failure_reason=None if resolved else "ranking endpoint is unavailable",
    )


def ranking_audit(*, complete=True):
    entry = AllocationRankingCapabilityEntry(
        allocation_id=0,
        country_id=26,
        country_name="England",
        endpoint_a=endpoint(0, resolved=True),
        endpoint_b=endpoint(2, resolved=complete),
    )
    return AllocationRankingCapabilityAudit(
        catalog_sha256=CATALOG,
        assigned_allocation_ids=(0,),
        resolved_allocation_ids=(0,) if complete else (),
        unresolved_allocation_ids=() if complete else (0,),
        required_endpoint_ids=(0, 2),
        resolved_endpoint_ids=(0, 2) if complete else (0,),
        unresolved_endpoint_ids=() if complete else (2,),
        entries=(entry,),
    )


def preview(audit=None):
    audit = ranking_audit() if audit is None else audit
    exchange = LeagueMembershipExchange(
        allocation_id=0,
        slot_index=0,
        club_a_id=1,
        club_b_id=2,
        membership_a_before=0,
        membership_b_before=2,
    )
    return PlayableAllocationPreview(
        catalog_sha256=CATALOG,
        assigned_allocation_ids=(0,),
        ranking_capability=audit,
        memberships_before={1: 0, 2: 2},
        memberships_after={1: 2, 2: 0},
        exchanges=(exchange,),
        country_summaries=(
            PlayableCountryExchangeSummary(
                country_id=26,
                country_name="England",
                allocation_ids=(0,),
                exchange_count=1,
                exchanged_club_ids=(1, 2),
            ),
        ),
    )


class Gate17FullScopePreflightTests(unittest.TestCase):
    def test_complete_independent_audits_are_ready_for_runtime_validation(self):
        ranking = ranking_audit()
        result = build_full_scope_preflight(
            human_audit(),
            ranking,
            preview(ranking),
        )

        self.assertTrue(result.ready_for_full_runtime_validation)
        self.assertEqual(result.blocker_codes, ())
        self.assertEqual(result.catalog_sha256, CATALOG)
        self.assertEqual(result.scope_entry_count, 1)
        self.assertEqual(result.supported_scope_ids, ("26:0",))
        self.assertEqual(result.unsupported_scope_ids, ())
        self.assertEqual(result.previewed_allocation_ids, (0,))
        payload = result.as_dict()
        self.assertTrue(payload["ready_for_full_runtime_validation"])
        self.assertEqual(payload["blocker_codes"], [])

    def test_incomplete_surfaces_remain_explicit_blockers(self):
        result = build_full_scope_preflight(
            human_audit(complete=False),
            ranking_audit(complete=False),
            None,
        )
        self.assertFalse(result.ready_for_full_runtime_validation)
        self.assertEqual(
            result.blocker_codes,
            (
                "human_scope_incomplete",
                "progression_rankings_incomplete",
                "allocation_preview_missing",
            ),
        )
        self.assertEqual(result.unsupported_scope_ids, ("26:0",))
        self.assertEqual(result.unresolved_allocation_ids, (0,))
        self.assertEqual(result.unresolved_ranking_endpoint_ids, (2,))
        self.assertFalse(result.allocation_preview_complete)

    def test_catalog_identity_must_match_across_all_inputs(self):
        ranking = ranking_audit()
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "different catalogs",
        ):
            build_full_scope_preflight(
                human_audit(),
                replace(ranking, catalog_sha256="d" * 64),
                None,
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "different playable-scope catalog",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                replace(preview(ranking), catalog_sha256="d" * 64),
            )

    def test_preview_must_be_from_exact_supplied_ranking_audit(self):
        ranking = ranking_audit()
        altered = replace(
            ranking,
            resolved_endpoint_ids=(2, 0),
        )
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "ranking audit does not match",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                preview(altered),
            )

    def test_preview_must_cover_exact_assigned_allocation_set(self):
        ranking = ranking_audit()
        bad_preview = replace(
            preview(ranking),
            assigned_allocation_ids=(0, 7),
        )
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact assigned allocation set",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                bad_preview,
            )

    def test_preview_exchange_membership_and_country_coverage_fail_closed(self):
        ranking = ranking_audit()
        base = preview(ranking)

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exchange ledger",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                replace(base, exchanges=()),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "membership key set changed",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                replace(base, memberships_after={1: 2}),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "country summaries",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                replace(base, country_summaries=()),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "duplicate assigned allocation IDs",
        ):
            build_full_scope_preflight(
                human_audit(),
                ranking,
                replace(base, assigned_allocation_ids=(0, 0)),
            )

    def test_empty_human_scope_and_bad_input_types_fail_closed(self):
        empty = replace(human_audit(), entries=())
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "contains no TeamSelect scope entries",
        ):
            build_full_scope_preflight(
                empty,
                ranking_audit(),
                None,
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact HumanScopeCapabilityAudit",
        ):
            build_full_scope_preflight(
                object(),
                ranking_audit(),
                None,
            )


if __name__ == "__main__":
    unittest.main()
