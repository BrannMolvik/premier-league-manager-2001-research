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
from gate17_multi_human_capability import (
    audit_multi_human_capability,
    run_current_multi_human_capability,
)
from gate17_playable_allocation_preview import (
    PlayableAllocationPreview,
    PlayableCountryExchangeSummary,
)
from gate17_runtime_owner_capability import (
    RuntimeOwnerCapabilityAudit,
    RuntimeOwnerCapabilityEntry,
)
from gate17_runtime_progression_audit import RuntimeProgressionAudit
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


def runtime_owner_audit(*, complete=True, scope_id="26:0"):
    blockers = () if complete else ("human_match_dispatch_missing",)
    entry = RuntimeOwnerCapabilityEntry(
        scope_id=scope_id,
        country_id=26,
        competition_id=0,
        runtime_owner="fixed_primary",
        selection_supported=True,
        runtime_materialized=True,
        human_match_supported=complete,
        fresh_financial_objective_supported=True,
        sporting_objective_progression_supported=True,
        annual_progression_supported=True,
        blocker_codes=blockers,
    )
    return RuntimeOwnerCapabilityAudit(
        catalog_sha256=CATALOG,
        entries=(entry,),
    )


def multi_human_audit(*, complete=True):
    return audit_multi_human_capability(
        teamselect_selection_capacity=6,
        gameplay_simultaneous_users_supported=6 if complete else 1,
        multi_human_start_supported=complete,
        shared_runtime_supported=complete,
        save_reload_supported=complete,
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


def progression_audit(*, complete=True, with_preview=True):
    ranking = ranking_audit(complete=complete)
    allocation_preview = preview(ranking) if complete and with_preview else None
    return RuntimeProgressionAudit(
        catalog_sha256=CATALOG,
        required_endpoint_ids=(0, 2),
        resolved_rankings={0: (1,), 2: (2,) if complete else None},
        ranking_capability=ranking,
        allocation_preview=allocation_preview,
        runtime_memberships_unchanged=True,
    )


class Gate17FullScopePreflightTests(unittest.TestCase):
    def test_complete_audits_are_ready_for_full_runtime_validation(self):
        result = build_full_scope_preflight(
            human_audit(),
            runtime_owner_audit(),
            multi_human_audit(),
            progression_audit(),
        )

        self.assertTrue(result.ready_for_full_runtime_validation)
        self.assertTrue(result.runtime_owner_complete)
        self.assertTrue(result.multi_human_complete)
        self.assertEqual(result.multi_human_required_users, 6)
        self.assertEqual(result.multi_human_gameplay_users_supported, 6)
        self.assertTrue(result.progression_runtime_complete)
        self.assertEqual(result.blocker_codes, ())
        self.assertEqual(result.supported_scope_ids, ("26:0",))
        self.assertEqual(result.runtime_owner_supported_scope_ids, ("26:0",))
        self.assertEqual(result.previewed_allocation_ids, (0,))
        self.assertEqual(result.as_dict()["schema_version"], 3)
        self.assertTrue(result.as_dict()["ready_for_full_runtime_validation"])

    def test_current_single_manager_backend_blocks_otherwise_ready_preflight(self):
        multi_human = run_current_multi_human_capability()
        result = build_full_scope_preflight(
            human_audit(),
            runtime_owner_audit(),
            multi_human,
            progression_audit(),
        )

        self.assertFalse(result.ready_for_full_runtime_validation)
        self.assertEqual(
            result.blocker_codes,
            ("multi_human_capability_incomplete",),
        )
        self.assertEqual(result.multi_human_required_users, 6)
        self.assertEqual(result.multi_human_gameplay_users_supported, 1)
        self.assertEqual(
            result.multi_human_blocker_codes,
            multi_human.blocker_codes,
        )

    def test_incomplete_surfaces_remain_explicit_blockers(self):
        result = build_full_scope_preflight(
            human_audit(complete=False),
            runtime_owner_audit(complete=False),
            multi_human_audit(complete=False),
            progression_audit(complete=False, with_preview=False),
        )

        self.assertFalse(result.ready_for_full_runtime_validation)
        self.assertEqual(
            result.blocker_codes,
            (
                "human_scope_incomplete",
                "runtime_owner_capability_incomplete",
                "multi_human_capability_incomplete",
                "progression_rankings_incomplete",
                "allocation_preview_missing",
            ),
        )
        self.assertEqual(result.unsupported_scope_ids, ("26:0",))
        self.assertEqual(result.runtime_owner_blocked_scope_ids, ("26:0",))
        self.assertEqual(
            result.runtime_owner_blocker_codes,
            ("human_match_dispatch_missing",),
        )
        self.assertFalse(result.multi_human_complete)
        self.assertIn(
            "multi_human_gameplay_capacity_incomplete",
            result.multi_human_blocker_codes,
        )
        self.assertEqual(result.unresolved_allocation_ids, (0,))
        self.assertEqual(result.unresolved_ranking_endpoint_ids, (2,))

    def test_catalog_identity_must_match_across_all_inputs(self):
        bad_owner = replace(runtime_owner_audit(), catalog_sha256="d" * 64)
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "runtime-owner audits target different catalogs",
        ):
            build_full_scope_preflight(
                human_audit(),
                bad_owner,
                multi_human_audit(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "different catalogs",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                multi_human_audit(),
                replace(progression_audit(), catalog_sha256="d" * 64),
            )

        bad_ranking = replace(
            progression_audit().ranking_capability,
            catalog_sha256="d" * 64,
        )
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "ranking capability",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                multi_human_audit(),
                replace(progression_audit(), ranking_capability=bad_ranking),
            )

    def test_runtime_owner_scope_identity_must_exactly_match_human_scope(self):
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "scope IDs do not exactly match",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(scope_id="66:27"),
                multi_human_audit(),
                progression_audit(),
            )

    def test_runtime_preview_integrity_must_match_runtime_audit(self):
        progression = progression_audit()
        altered_ranking = replace(
            progression.ranking_capability,
            resolved_endpoint_ids=(2, 0),
        )
        bad_preview = replace(
            progression.allocation_preview,
            ranking_capability=altered_ranking,
        )
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "ranking audit does not match",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                multi_human_audit(),
                replace(progression, allocation_preview=bad_preview),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact assigned allocation set",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                multi_human_audit(),
                replace(
                    progression,
                    allocation_preview=replace(
                        progression.allocation_preview,
                        assigned_allocation_ids=(0, 7),
                    ),
                ),
            )

    def test_membership_mutation_flag_is_an_explicit_blocker(self):
        progression = replace(
            progression_audit(),
            runtime_memberships_unchanged=False,
        )
        result = build_full_scope_preflight(
            human_audit(),
            runtime_owner_audit(),
            multi_human_audit(),
            progression,
        )

        self.assertFalse(result.ready_for_full_runtime_validation)
        self.assertIn("runtime_membership_mutation", result.blocker_codes)

    def test_empty_audits_and_bad_types_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "human-scope audit contains no TeamSelect scope entries",
        ):
            build_full_scope_preflight(
                replace(human_audit(), entries=()),
                runtime_owner_audit(),
                multi_human_audit(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "runtime-owner audit contains no TeamSelect scope entries",
        ):
            build_full_scope_preflight(
                human_audit(),
                replace(runtime_owner_audit(), entries=()),
                multi_human_audit(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact HumanScopeCapabilityAudit",
        ):
            build_full_scope_preflight(
                object(),
                runtime_owner_audit(),
                multi_human_audit(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact RuntimeOwnerCapabilityAudit",
        ):
            build_full_scope_preflight(
                human_audit(),
                object(),
                multi_human_audit(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact MultiHumanCapabilityAudit",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                object(),
                progression_audit(),
            )

        with self.assertRaisesRegex(
            Gate17FullScopePreflightError,
            "exact RuntimeProgressionAudit",
        ):
            build_full_scope_preflight(
                human_audit(),
                runtime_owner_audit(),
                multi_human_audit(),
                object(),
            )


if __name__ == "__main__":
    unittest.main()
