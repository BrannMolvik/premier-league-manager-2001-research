"""Tests for the fail-closed Gate-17 objective RNG adjudication plan."""
import unittest

from gate17_objective_rng_adjudication import (
    STAGE_DRAW_POSITION,
    STAGE_ENTRY_CRT_STATE,
    STAGE_SETUP_OWNER,
    Gate17ObjectiveRngAdjudicationError,
    build_objective_rng_adjudication_plan,
    objective_rng_adjudication_contract,
)


def neutral_trace_report() -> dict:
    direct_names = (
        "objective_setup",
        "fresh_objective_generator",
        "shared_crt_bounded_rng",
        "hierarchy_class_helper",
        "first_class_helper",
        "last_class_equal_helper",
        "promotion_playoff_status_helper",
    )
    return {
        "source_sha256": "a" * 64,
        "source_contract": {
            "dbruser_constructor_va": 0x425680,
            "objective_setup_va": 0x5DF670,
            "fresh_objective_generator_va": 0x5DFD30,
            "shared_crt_bounded_rng_va": 0x64D540,
            "hierarchy_class_helper_va": 0x4FA520,
            "first_class_helper_va": 0x4FA570,
            "last_class_equal_helper_va": 0x4FA590,
            "promotion_playoff_status_helper_va": 0x4F88C0,
            "objective_rng_bound": 100,
            "objective_rng_lower_branch_max_inclusive": 50,
            "objective_setup_slot_count": 3,
            "fresh_branch_table_recovered": True,
            "deterministic_non_pl_branches_materializable": True,
            "rng_bearing_branches_require_shared_crt_state": True,
        },
        "direct_call_candidates": [
            {
                "target_name": name,
                "target_va": 0x401000 + index * 0x10,
                "decoded_direct_calls_not_objective_rng_semantic_proof": [
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
        "objective_setup_callers_classified": False,
        "objective_setup_entry_crt_state_recovered": False,
        "rng_bearing_branch_draw_position_recovered": False,
        "fresh_objective_rng_replay_ready": False,
        "all_playable_scope_fresh_objectives_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }


class Gate17ObjectiveRngAdjudicationTests(unittest.TestCase):
    def test_exact_three_stage_order_stays_fail_closed(self):
        plan = build_objective_rng_adjudication_plan(neutral_trace_report())
        self.assertEqual(
            tuple(stage.stage for stage in plan.stages),
            (
                STAGE_SETUP_OWNER,
                STAGE_ENTRY_CRT_STATE,
                STAGE_DRAW_POSITION,
            ),
        )
        self.assertEqual(
            tuple(stage.priority for stage in plan.stages),
            (1, 2, 3),
        )
        self.assertTrue(
            all(stage.status == "needs_private_source" for stage in plan.stages)
        )
        self.assertFalse(plan.trace_candidates_are_objective_rng_semantic_proof)
        self.assertFalse(plan.fresh_objective_rng_replay_ready)
        self.assertFalse(plan.all_playable_scope_fresh_objectives_ready)
        self.assertFalse(plan.gate17_full_scope_ready)
        self.assertFalse(plan.gate17_complete)

    def test_setup_owner_must_be_proved_before_crt_state(self):
        plan = build_objective_rng_adjudication_plan(neutral_trace_report())
        first, second, third = plan.stages
        self.assertEqual(first.stage, STAGE_SETUP_OWNER)
        self.assertEqual(second.stage, STAGE_ENTRY_CRT_STATE)
        self.assertEqual(third.stage, STAGE_DRAW_POSITION)
        self.assertIn(
            "objective_setup_callers_classified",
            first.capability_flags_unlocked_only_after_proof,
        )
        self.assertIn(
            "objective_setup_entry_crt_state_recovered",
            second.capability_flags_unlocked_only_after_proof,
        )
        self.assertIn(
            "rng_bearing_branch_draw_position_recovered",
            third.capability_flags_unlocked_only_after_proof,
        )

    def test_neutral_trace_flags_cannot_be_pre_promoted(self):
        for key in (
            "objective_setup_callers_classified",
            "objective_setup_entry_crt_state_recovered",
            "rng_bearing_branch_draw_position_recovered",
            "fresh_objective_rng_replay_ready",
            "all_playable_scope_fresh_objectives_ready",
            "gate17_full_scope_ready",
            "gate17_complete",
        ):
            report = neutral_trace_report()
            report[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17ObjectiveRngAdjudicationError,
                    "must keep",
                ):
                    build_objective_rng_adjudication_plan(report)

    def test_exact_source_anchor_contract_cannot_drift(self):
        cases = (
            ("dbruser_constructor_va", 0x425681),
            ("objective_setup_va", 0x5DF671),
            ("fresh_objective_generator_va", 0x5DFD31),
            ("shared_crt_bounded_rng_va", 0x64D541),
            ("hierarchy_class_helper_va", 0x4FA521),
            ("first_class_helper_va", 0x4FA571),
            ("last_class_equal_helper_va", 0x4FA591),
            ("promotion_playoff_status_helper_va", 0x4F88C1),
            ("objective_rng_bound", 99),
            ("objective_rng_lower_branch_max_inclusive", 49),
            ("objective_setup_slot_count", 2),
        )
        for key, value in cases:
            report = neutral_trace_report()
            report["source_contract"][key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17ObjectiveRngAdjudicationError,
                    "source contract drifted",
                ):
                    build_objective_rng_adjudication_plan(report)

    def test_required_source_truths_cannot_be_weakened(self):
        for key in (
            "fresh_branch_table_recovered",
            "deterministic_non_pl_branches_materializable",
            "rng_bearing_branches_require_shared_crt_state",
        ):
            report = neutral_trace_report()
            report["source_contract"][key] = False
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17ObjectiveRngAdjudicationError,
                    "must retain source-proven",
                ):
                    build_objective_rng_adjudication_plan(report)

    def test_missing_required_candidate_family_fails_closed(self):
        report = neutral_trace_report()
        report["direct_call_candidates"] = [
            row
            for row in report["direct_call_candidates"]
            if row["target_name"] != "shared_crt_bounded_rng"
        ]
        with self.assertRaisesRegex(
            Gate17ObjectiveRngAdjudicationError,
            "missing required objective RNG candidate families",
        ):
            build_objective_rng_adjudication_plan(report)

    def test_candidate_classification_cannot_be_upgraded(self):
        report = neutral_trace_report()
        report["direct_call_candidates"][0][
            "decoded_direct_calls_not_objective_rng_semantic_proof"
        ][0]["classification"] = "proven_objective_rng_semantics"
        with self.assertRaisesRegex(
            Gate17ObjectiveRngAdjudicationError,
            "lost its non-semantic classification",
        ):
            build_objective_rng_adjudication_plan(report)

    def test_contract_keeps_runtime_integration_separate(self):
        contract = objective_rng_adjudication_contract()
        self.assertEqual(contract["source_objective_rng_bound"], 100)
        self.assertEqual(contract["source_lower_branch_max_inclusive"], 50)
        self.assertEqual(contract["source_setup_slot_count"], 3)
        self.assertFalse(contract["candidate_calls_are_objective_rng_semantics"])
        self.assertTrue(contract["private_source_required_for_stage_completion"])
        self.assertTrue(contract["runtime_integration_after_source_required"])
        self.assertFalse(contract["fresh_objective_rng_replay_ready"])
        self.assertFalse(contract["all_playable_scope_fresh_objectives_ready"])
        self.assertFalse(contract["gate17_full_scope_ready"])
        self.assertFalse(contract["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
