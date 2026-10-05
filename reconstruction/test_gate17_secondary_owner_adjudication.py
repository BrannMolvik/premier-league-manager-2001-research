"""Tests for the fail-closed Gate-17 secondary-owner adjudication plan."""
import unittest

from gate17_secondary_owner_adjudication import (
    STAGE_DAILY_RUNTIME_OWNER,
    STAGE_HUMAN_MATCH_DISPATCH,
    STAGE_SAVE_RELOAD,
    STAGE_SEASON_CONTINUATION,
    Gate17SecondaryOwnerAdjudicationError,
    adjudication_plan_contract,
    build_secondary_owner_adjudication_plan,
)


def neutral_report() -> dict:
    direct_names = (
        "schedule_container_selector",
        "schedule_container_insert",
        "schedule_container_final_shuffle",
        "schedule_container_runtime_traversal",
        "schedule_container_build",
        "schedule_container_later_finalization",
    )
    return {
        "source_sha256": "a" * 64,
        "direct_call_candidates": [
            {
                "target_name": name,
                "target_va": 0x401000 + index * 0x10,
                "decoded_direct_calls_not_lifecycle_semantic_proof": [
                    {
                        "callsite_va": 0x402000 + index * 0x10,
                        "target_va": 0x401000 + index * 0x10,
                        "section": ".text",
                        "classification": (
                            "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
                        ),
                    }
                ],
            }
            for index, name in enumerate(direct_names)
        ],
        "global_candidates": [
            {
                "target_name": "primary_schedule_container_global",
                "target_va": 0x947AD8,
                "byte_occurrences_not_proven_xrefs": [],
            },
            {
                "target_name": "secondary_schedule_container_global",
                "target_va": 0x947AF0,
                "byte_occurrences_not_proven_xrefs": [],
            },
        ],
        "live_secondary_runtime_owner_recovered": False,
        "live_secondary_daily_execution_binding_recovered": False,
        "secondary_season_continuation_recovered": False,
        "secondary_human_match_dispatch_recovered": False,
        "secondary_save_serialization_recovered": False,
        "secondary_save_reload_continuation_recovered": False,
        "procedural_secondary_scope_playable": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }


class Gate17SecondaryOwnerAdjudicationTests(unittest.TestCase):
    def test_plan_has_exact_priority_order_and_stays_fail_closed(self):
        plan = build_secondary_owner_adjudication_plan(neutral_report())
        self.assertEqual(
            tuple(stage.stage for stage in plan.stages),
            (
                STAGE_DAILY_RUNTIME_OWNER,
                STAGE_SEASON_CONTINUATION,
                STAGE_HUMAN_MATCH_DISPATCH,
                STAGE_SAVE_RELOAD,
            ),
        )
        self.assertEqual(
            tuple(stage.priority for stage in plan.stages),
            (1, 2, 3, 4),
        )
        self.assertTrue(all(stage.status == "needs_private_source" for stage in plan.stages))
        self.assertFalse(plan.trace_candidates_are_semantic_proof)
        self.assertFalse(plan.secondary_runtime_owner_recovered)
        self.assertFalse(plan.procedural_secondary_scope_playable)
        self.assertFalse(plan.gate17_complete)

    def test_daily_stage_requires_receiver_or_secondary_global_proof(self):
        plan = build_secondary_owner_adjudication_plan(neutral_report())
        daily = plan.stages[0]
        self.assertEqual(daily.stage, STAGE_DAILY_RUNTIME_OWNER)
        self.assertIn(
            "schedule_container_runtime_traversal",
            daily.candidate_target_names,
        )
        self.assertIn(
            "secondary_schedule_container_global",
            daily.candidate_target_names,
        )
        self.assertIn(
            "live_secondary_runtime_owner_recovered",
            daily.capability_flags_unlocked_only_after_proof,
        )
        self.assertIn(
            "live_secondary_daily_execution_binding_recovered",
            daily.capability_flags_unlocked_only_after_proof,
        )

    def test_later_stages_keep_human_and_persistence_separate(self):
        plan = build_secondary_owner_adjudication_plan(neutral_report())
        season, human, persistence = plan.stages[1:]
        self.assertEqual(season.stage, STAGE_SEASON_CONTINUATION)
        self.assertEqual(human.stage, STAGE_HUMAN_MATCH_DISPATCH)
        self.assertEqual(persistence.stage, STAGE_SAVE_RELOAD)
        self.assertNotEqual(
            human.capability_flags_unlocked_only_after_proof,
            persistence.capability_flags_unlocked_only_after_proof,
        )
        self.assertIn(
            "secondary_save_reload_continuation_recovered",
            persistence.capability_flags_unlocked_only_after_proof,
        )

    def test_trace_must_remain_neutral(self):
        for key in (
            "live_secondary_runtime_owner_recovered",
            "secondary_season_continuation_recovered",
            "procedural_secondary_scope_playable",
            "gate17_complete",
        ):
            report = neutral_report()
            report[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17SecondaryOwnerAdjudicationError,
                    "must keep",
                ):
                    build_secondary_owner_adjudication_plan(report)

    def test_missing_required_candidate_family_fails_closed(self):
        report = neutral_report()
        report["direct_call_candidates"] = [
            row
            for row in report["direct_call_candidates"]
            if row["target_name"] != "schedule_container_runtime_traversal"
        ]
        with self.assertRaisesRegex(
            Gate17SecondaryOwnerAdjudicationError,
            "missing required candidate families",
        ):
            build_secondary_owner_adjudication_plan(report)

    def test_candidate_classification_cannot_be_upgraded(self):
        report = neutral_report()
        row = report["direct_call_candidates"][0]
        row["decoded_direct_calls_not_lifecycle_semantic_proof"][0][
            "classification"
        ] = "proven_runtime_owner"
        with self.assertRaisesRegex(
            Gate17SecondaryOwnerAdjudicationError,
            "lost its non-semantic classification",
        ):
            build_secondary_owner_adjudication_plan(report)

    def test_contract_names_private_source_boundary(self):
        contract = adjudication_plan_contract()
        self.assertEqual(
            contract["stage_order"],
            (
                STAGE_DAILY_RUNTIME_OWNER,
                STAGE_SEASON_CONTINUATION,
                STAGE_HUMAN_MATCH_DISPATCH,
                STAGE_SAVE_RELOAD,
            ),
        )
        self.assertFalse(contract["raw_global_candidates_are_xrefs"])
        self.assertFalse(contract["decoded_direct_calls_are_lifecycle_semantics"])
        self.assertTrue(contract["private_source_required_for_stage_completion"])
        self.assertFalse(contract["procedural_secondary_scope_playable"])
        self.assertFalse(contract["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
