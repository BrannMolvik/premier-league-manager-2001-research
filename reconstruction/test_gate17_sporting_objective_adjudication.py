"""Tests for the fail-closed Gate-17 sporting-objective adjudication plan."""
import unittest

from gate17_sporting_objective_adjudication import (
    STAGE_ANNUAL_OWNER,
    STAGE_NON_PL_BRANCHES,
    STAGE_STATE_UPDATE,
    Gate17SportingObjectiveAdjudicationError,
    build_sporting_objective_adjudication_plan,
    sporting_objective_adjudication_contract,
)


def neutral_trace_report() -> dict:
    names = (
        "sporting_objective_progression",
        "sporting_objective_branch",
        "sporting_objective_classification_compare",
        "annual_objective_evaluation",
        "dbruser_sacking_reason_setter",
    )
    return {
        "source_sha256": "a" * 64,
        "source_contract": {
            "annual_competition_transition_va": 0x4A8628,
            "sporting_objective_progress_va": 0x5E1C00,
            "sporting_objective_branch_va": 0x5E0310,
            "sporting_objective_classification_compare_va": 0x5E07E4,
            "between_progression_passes_transition_va": 0x4F9010,
            "annual_objective_evaluation_caller_va": 0x426220,
            "annual_objective_evaluation_va": 0x5E1D90,
            "dbruser_sacking_reason_setter_va": 0x42C6C0,
            "objective_selected_id_offset": 0x64,
            "objective_progression_gate_offset": 0x68,
            "objective_progression_state_offset": 0x9C,
            "sporting_objective_switch_case_count": 17,
            "sporting_objective_pass_sequence": (1, 0),
            "same_premier_league_slice_recovered": True,
            "annual_evaluation_year_gate_recovered": True,
        },
        "direct_call_candidates": [
            {
                "target_name": name,
                "target_va": 0x401000 + index * 0x10,
                "decoded_direct_calls_not_sporting_progression_semantic_proof": [
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
            for index, name in enumerate(names)
        ],
        "annual_sporting_owner_chronology_recovered": False,
        "non_pl_objective_branch_table_recovered": False,
        "promotion_relegation_classification_semantics_recovered": False,
        "non_pl_progression_gate_update_recovered": False,
        "non_pl_sporting_objective_progression_ready": False,
        "all_playable_scope_sporting_progression_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }


class Gate17SportingObjectiveAdjudicationTests(unittest.TestCase):
    def test_exact_three_stage_order_stays_fail_closed(self):
        plan = build_sporting_objective_adjudication_plan(neutral_trace_report())
        self.assertEqual(
            tuple(stage.stage for stage in plan.stages),
            (STAGE_ANNUAL_OWNER, STAGE_NON_PL_BRANCHES, STAGE_STATE_UPDATE),
        )
        self.assertEqual(tuple(stage.priority for stage in plan.stages), (1, 2, 3))
        self.assertTrue(
            all(stage.status == "needs_private_source" for stage in plan.stages)
        )
        self.assertFalse(plan.trace_candidates_are_sporting_semantic_proof)
        self.assertFalse(plan.non_pl_sporting_objective_progression_ready)
        self.assertFalse(plan.all_playable_scope_sporting_progression_ready)
        self.assertFalse(plan.gate17_full_scope_ready)
        self.assertFalse(plan.gate17_complete)

    def test_stage_capability_boundaries_are_separate(self):
        plan = build_sporting_objective_adjudication_plan(neutral_trace_report())
        first, second, third = plan.stages
        self.assertEqual(
            first.capability_flags_unlocked_only_after_proof,
            ("annual_sporting_owner_chronology_recovered",),
        )
        self.assertEqual(
            second.capability_flags_unlocked_only_after_proof,
            (
                "non_pl_objective_branch_table_recovered",
                "promotion_relegation_classification_semantics_recovered",
            ),
        )
        self.assertEqual(
            third.capability_flags_unlocked_only_after_proof,
            ("non_pl_progression_gate_update_recovered",),
        )

    def test_neutral_flags_cannot_be_pre_promoted(self):
        for key in (
            "annual_sporting_owner_chronology_recovered",
            "non_pl_objective_branch_table_recovered",
            "promotion_relegation_classification_semantics_recovered",
            "non_pl_progression_gate_update_recovered",
            "non_pl_sporting_objective_progression_ready",
            "all_playable_scope_sporting_progression_ready",
            "gate17_full_scope_ready",
            "gate17_complete",
        ):
            report = neutral_trace_report()
            report[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17SportingObjectiveAdjudicationError,
                    "must keep",
                ):
                    build_sporting_objective_adjudication_plan(report)

    def test_exact_source_contract_cannot_drift(self):
        cases = (
            ("annual_competition_transition_va", 0x4A8629),
            ("sporting_objective_progress_va", 0x5E1C01),
            ("sporting_objective_branch_va", 0x5E0311),
            ("sporting_objective_classification_compare_va", 0x5E07E5),
            ("between_progression_passes_transition_va", 0x4F9011),
            ("annual_objective_evaluation_caller_va", 0x426221),
            ("annual_objective_evaluation_va", 0x5E1D91),
            ("dbruser_sacking_reason_setter_va", 0x42C6C1),
            ("objective_selected_id_offset", 0x65),
            ("objective_progression_gate_offset", 0x69),
            ("objective_progression_state_offset", 0x9D),
            ("sporting_objective_switch_case_count", 16),
            ("sporting_objective_pass_sequence", (0, 1)),
        )
        for key, value in cases:
            report = neutral_trace_report()
            report["source_contract"][key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17SportingObjectiveAdjudicationError,
                    "source contract drifted",
                ):
                    build_sporting_objective_adjudication_plan(report)

    def test_source_truths_cannot_be_weakened(self):
        for key in (
            "same_premier_league_slice_recovered",
            "annual_evaluation_year_gate_recovered",
        ):
            report = neutral_trace_report()
            report["source_contract"][key] = False
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17SportingObjectiveAdjudicationError,
                    "must retain source-proven",
                ):
                    build_sporting_objective_adjudication_plan(report)

    def test_missing_candidate_family_fails_closed(self):
        report = neutral_trace_report()
        report["direct_call_candidates"] = [
            row
            for row in report["direct_call_candidates"]
            if row["target_name"] != "sporting_objective_classification_compare"
        ]
        with self.assertRaisesRegex(
            Gate17SportingObjectiveAdjudicationError,
            "missing required sporting candidate families",
        ):
            build_sporting_objective_adjudication_plan(report)

    def test_candidate_classification_cannot_be_upgraded(self):
        report = neutral_trace_report()
        report["direct_call_candidates"][0][
            "decoded_direct_calls_not_sporting_progression_semantic_proof"
        ][0]["classification"] = "proven_sporting_semantics"
        with self.assertRaisesRegex(
            Gate17SportingObjectiveAdjudicationError,
            "lost its non-semantic classification",
        ):
            build_sporting_objective_adjudication_plan(report)

    def test_contract_keeps_runtime_integration_separate(self):
        contract = sporting_objective_adjudication_contract()
        self.assertEqual(contract["source_switch_case_count"], 17)
        self.assertEqual(contract["source_pass_sequence"], (1, 0))
        self.assertFalse(contract["candidate_calls_are_sporting_semantics"])
        self.assertTrue(contract["private_source_required_for_stage_completion"])
        self.assertTrue(contract["runtime_integration_after_source_required"])
        self.assertFalse(contract["non_pl_sporting_objective_progression_ready"])
        self.assertFalse(contract["all_playable_scope_sporting_progression_ready"])
        self.assertFalse(contract["gate17_full_scope_ready"])
        self.assertFalse(contract["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
