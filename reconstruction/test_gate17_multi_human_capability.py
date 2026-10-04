"""Tests for the Gate-17 source-proven multi-human capability audit."""
import unittest

from gate17_multi_human_capability import (
    Gate17MultiHumanCapabilityError,
    ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS,
    audit_multi_human_capability,
    run_current_multi_human_capability,
)


class Gate17MultiHumanCapabilityTests(unittest.TestCase):
    def test_complete_six_user_surface_has_no_blockers(self):
        audit = audit_multi_human_capability(
            teamselect_selection_capacity=6,
            gameplay_simultaneous_users_supported=6,
            multi_human_start_supported=True,
            shared_runtime_supported=True,
            save_reload_supported=True,
        )

        self.assertEqual(audit.required_simultaneous_users, 6)
        self.assertTrue(audit.complete)
        self.assertEqual(audit.blocker_codes, ())
        self.assertTrue(audit.as_dict()["complete"])
        self.assertEqual(audit.as_dict()["schema_version"], 1)

    def test_current_single_manager_surface_remains_fail_closed(self):
        audit = run_current_multi_human_capability()

        self.assertEqual(
            audit.required_simultaneous_users,
            ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS,
        )
        self.assertEqual(audit.teamselect_selection_capacity, 6)
        self.assertEqual(audit.gameplay_simultaneous_users_supported, 1)
        self.assertFalse(audit.complete)
        self.assertEqual(
            audit.blocker_codes,
            (
                "multi_human_gameplay_capacity_incomplete",
                "multi_human_start_missing",
                "shared_multi_human_runtime_missing",
                "multi_human_save_reload_missing",
            ),
        )

    def test_every_dimension_is_independently_fail_closed(self):
        audit = audit_multi_human_capability(
            teamselect_selection_capacity=5,
            gameplay_simultaneous_users_supported=5,
            multi_human_start_supported=False,
            shared_runtime_supported=False,
            save_reload_supported=False,
        )
        self.assertEqual(
            audit.blocker_codes,
            (
                "teamselect_multi_human_selection_incomplete",
                "multi_human_gameplay_capacity_incomplete",
                "multi_human_start_missing",
                "shared_multi_human_runtime_missing",
                "multi_human_save_reload_missing",
            ),
        )

    def test_invalid_types_and_counts_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17MultiHumanCapabilityError,
            "required_simultaneous_users",
        ):
            audit_multi_human_capability(
                required_simultaneous_users=True,
                teamselect_selection_capacity=6,
                gameplay_simultaneous_users_supported=6,
                multi_human_start_supported=True,
                shared_runtime_supported=True,
                save_reload_supported=True,
            )
        with self.assertRaisesRegex(
            Gate17MultiHumanCapabilityError,
            "teamselect_selection_capacity",
        ):
            audit_multi_human_capability(
                teamselect_selection_capacity=0,
                gameplay_simultaneous_users_supported=1,
                multi_human_start_supported=False,
                shared_runtime_supported=False,
                save_reload_supported=False,
            )
        with self.assertRaisesRegex(
            Gate17MultiHumanCapabilityError,
            "multi_human_start_supported",
        ):
            audit_multi_human_capability(
                teamselect_selection_capacity=6,
                gameplay_simultaneous_users_supported=1,
                multi_human_start_supported=1,
                shared_runtime_supported=False,
                save_reload_supported=False,
            )


if __name__ == "__main__":
    unittest.main()
