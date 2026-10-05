"""Tests for the fail-closed Gate-17 multi-human adjudication plan."""
import unittest

from gate17_multi_human_adjudication import (
    STAGE_FIXTURE_DISPATCH,
    STAGE_SAVE_RELOAD,
    STAGE_SHARED_RUNTIME,
    STAGE_START_ITERATION,
    Gate17MultiHumanAdjudicationError,
    build_multi_human_adjudication_plan,
    multi_human_adjudication_contract,
)


def neutral_trace_report() -> dict:
    direct_names = (
        "teamselect_start_continuation",
        "user_lookup_current",
        "user_lookup_indexed",
        "user_create_append",
        "user_remove",
        "user_remove_final",
    )
    return {
        "source_sha256": "a" * 64,
        "source_contract": {
            "teamselect_start_event_va": 0x4DA480,
            "teamselect_start_continuation_va": 0x4C41C0,
            "teamselect_saturation_va": 0x4DA4D0,
            "global_user_count_va": 0x8755E4,
            "user_selected_club_pointer_offset": 0x5B4,
            "source_proven_hard_user_cap": 6,
            "selection_appends_users_recovered": True,
            "start_consumes_existing_user_list_recovered": True,
        },
        "global_candidates": [
            {
                "target_name": "global_user_count",
                "target_va": 0x8755E4,
                "byte_occurrences_not_proven_xrefs": [],
            }
        ],
        "direct_call_candidates": [
            {
                "target_name": name,
                "target_va": 0x401000 + index * 0x10,
                "decoded_direct_calls_not_handoff_semantic_proof": [
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
        "ordered_multi_user_start_iteration_recovered": False,
        "shared_multi_human_runtime_owner_recovered": False,
        "simultaneous_human_fixture_dispatch_order_recovered": False,
        "multi_human_save_serialization_recovered": False,
        "multi_human_save_reload_continuation_recovered": False,
        "multi_human_gameplay_supported": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }


class Gate17MultiHumanAdjudicationTests(unittest.TestCase):
    def test_exact_four_stage_priority_order_stays_fail_closed(self):
        plan = build_multi_human_adjudication_plan(neutral_trace_report())
        self.assertEqual(plan.source_proven_hard_user_cap, 6)
        self.assertEqual(
            tuple(stage.stage for stage in plan.stages),
            (
                STAGE_START_ITERATION,
                STAGE_SHARED_RUNTIME,
                STAGE_FIXTURE_DISPATCH,
                STAGE_SAVE_RELOAD,
            ),
        )
        self.assertEqual(tuple(stage.priority for stage in plan.stages), (1, 2, 3, 4))
        self.assertTrue(all(stage.status == "needs_private_source" for stage in plan.stages))
        self.assertFalse(plan.trace_candidates_are_handoff_semantic_proof)
        self.assertFalse(plan.multi_human_start_supported)
        self.assertFalse(plan.shared_runtime_supported)
        self.assertFalse(plan.save_reload_supported)
        self.assertFalse(plan.multi_human_gameplay_supported)
        self.assertFalse(plan.gate17_complete)

    def test_start_iteration_is_first_and_unlocks_no_runtime_without_proof(self):
        stage = build_multi_human_adjudication_plan(neutral_trace_report()).stages[0]
        self.assertEqual(stage.stage, STAGE_START_ITERATION)
        self.assertIn("teamselect_start_continuation", stage.candidate_target_names)
        self.assertIn("global_user_count", stage.candidate_target_names)
        self.assertIn(
            "multi_human_start_supported",
            stage.capability_dimensions_unlocked_only_after_proof,
        )
        self.assertIn(
            "gameplay_simultaneous_users_supported",
            stage.capability_dimensions_unlocked_only_after_proof,
        )

    def test_fixture_and_save_proofs_are_not_collapsed_into_start(self):
        plan = build_multi_human_adjudication_plan(neutral_trace_report())
        fixture = plan.stages[2]
        save = plan.stages[3]
        self.assertEqual(fixture.stage, STAGE_FIXTURE_DISPATCH)
        self.assertEqual(save.stage, STAGE_SAVE_RELOAD)
        self.assertIn(
            "simultaneous_human_fixture_dispatch_order_recovered",
            fixture.capability_dimensions_unlocked_only_after_proof,
        )
        self.assertIn(
            "multi_human_save_reload_continuation_recovered",
            save.capability_dimensions_unlocked_only_after_proof,
        )

    def test_neutral_trace_flags_cannot_be_pre_promoted(self):
        for key in (
            "ordered_multi_user_start_iteration_recovered",
            "shared_multi_human_runtime_owner_recovered",
            "simultaneous_human_fixture_dispatch_order_recovered",
            "multi_human_save_serialization_recovered",
            "multi_human_save_reload_continuation_recovered",
            "multi_human_gameplay_supported",
            "gate17_full_scope_ready",
            "gate17_complete",
        ):
            report = neutral_trace_report()
            report[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17MultiHumanAdjudicationError,
                    "must keep",
                ):
                    build_multi_human_adjudication_plan(report)

    def test_source_proven_six_user_contract_cannot_drift(self):
        report = neutral_trace_report()
        report["source_contract"]["source_proven_hard_user_cap"] = 5
        with self.assertRaisesRegex(
            Gate17MultiHumanAdjudicationError,
            "drifted from six",
        ):
            build_multi_human_adjudication_plan(report)

    def test_exact_source_anchor_contract_cannot_drift(self):
        cases = (
            ("teamselect_start_event_va", 0x4DA481),
            ("teamselect_start_continuation_va", 0x4C41C1),
            ("teamselect_saturation_va", 0x4DA4D1),
            ("global_user_count_va", 0x8755E8),
            ("user_selected_club_pointer_offset", 0x5B8),
        )
        for key, value in cases:
            report = neutral_trace_report()
            report["source_contract"][key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    Gate17MultiHumanAdjudicationError,
                    "source contract drifted",
                ):
                    build_multi_human_adjudication_plan(report)

    def test_missing_required_candidate_family_fails_closed(self):
        report = neutral_trace_report()
        report["direct_call_candidates"] = [
            row for row in report["direct_call_candidates"]
            if row["target_name"] != "user_lookup_indexed"
        ]
        with self.assertRaisesRegex(
            Gate17MultiHumanAdjudicationError,
            "missing required multi-human candidate families",
        ):
            build_multi_human_adjudication_plan(report)

    def test_candidate_classification_cannot_be_upgraded(self):
        report = neutral_trace_report()
        report["direct_call_candidates"][0][
            "decoded_direct_calls_not_handoff_semantic_proof"
        ][0]["classification"] = "proven_handoff"
        with self.assertRaisesRegex(
            Gate17MultiHumanAdjudicationError,
            "lost its non-semantic classification",
        ):
            build_multi_human_adjudication_plan(report)

    def test_contract_matches_current_single_manager_capability(self):
        contract = multi_human_adjudication_contract()
        self.assertEqual(contract["source_proven_hard_user_cap"], 6)
        self.assertEqual(contract["current_gameplay_simultaneous_users_supported"], 1)
        self.assertFalse(contract["candidate_calls_are_handoff_semantics"])
        self.assertFalse(contract["raw_global_occurrences_are_xrefs"])
        self.assertTrue(contract["private_source_required_for_stage_completion"])
        self.assertFalse(contract["current_multi_human_start_supported"])
        self.assertFalse(contract["current_shared_runtime_supported"])
        self.assertFalse(contract["current_save_reload_supported"])
        self.assertFalse(contract["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
