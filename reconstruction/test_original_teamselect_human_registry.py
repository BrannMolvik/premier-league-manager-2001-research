"""Unit tests for original source-only registered human list projection."""
import unittest

from original_teamselect_human_registry import (
    OriginalRegisteredHumanRegistry, OriginalTeamSelectHumanRegistryError,
)


class OriginalRegisteredHumanRegistryTests(unittest.TestCase):
    def test_fresh_native_owner_flag_and_append_order(self):
        r = OriginalRegisteredHumanRegistry()
        self.assertEqual(r.user_list_payload_deletion_flag, 1)
        self.assertEqual(r.current_index, 0)
        r, created = r.register(10, 100)
        self.assertTrue(created)
        self.assertEqual(r.current_index, 0)
        r, created = r.register(20, 200)
        self.assertTrue(created)
        self.assertEqual(r.current_index, 1)
        self.assertEqual(tuple(x.club_id for x in r.records), (10, 20))
        self.assertEqual(len(r.records), 2)

    def test_duplicate_club_noop_and_no_duplicate_user(self):
        r, _ = OriginalRegisteredHumanRegistry().register(10, 100)
        updated, created = r.register(10, 999)
        self.assertFalse(created)
        self.assertIs(updated, r)
        with self.assertRaises(OriginalTeamSelectHumanRegistryError):
            r.register(20, 100)

    def test_deselect_disposes_user_and_node_not_just_modal(self):
        r, _ = OriginalRegisteredHumanRegistry().register(10, 100)
        r, _ = r.register(20, 200)
        removal = r.deselect(10)
        self.assertEqual(removal.removed_index, 0)
        self.assertEqual(removal.removed.source_user_token, 100)
        self.assertTrue(removal.native_node_disposed)
        self.assertTrue(removal.native_user_payload_destructor_called)
        self.assertEqual(removal.native_staff_list_payload_deletion_flags, (1, 1, 0))
        self.assertEqual(removal.updated.current_index, 0)
        self.assertEqual(tuple(x.club_id for x in removal.updated.records), (20,))
        last = removal.updated.deselect(20)
        self.assertEqual(last.updated.current_index, -1)
        self.assertEqual(last.updated.records, ())
        again, _ = last.updated.register(30, 300)
        self.assertEqual(again.current_index, 0)

    def test_nonowning_list_unlinks_node_without_payload_destructor(self):
        r = OriginalRegisteredHumanRegistry(user_list_payload_deletion_flag=0)
        r, _ = r.register(10, 100)
        removal = r.deselect(10)
        self.assertTrue(removal.native_node_disposed)
        self.assertFalse(removal.native_user_payload_destructor_called)
        self.assertIsNone(removal.native_staff_list_payload_deletion_flags)
        self.assertEqual(removal.updated.records, ())

    def test_missing_user_and_seventh_human_fail_closed(self):
        r = OriginalRegisteredHumanRegistry()
        with self.assertRaises(OriginalTeamSelectHumanRegistryError):
            r.deselect(10)
        for index in range(6):
            r, accepted = r.register(index, index + 100)
            self.assertTrue(accepted)
        with self.assertRaises(OriginalTeamSelectHumanRegistryError):
            r.register(99, 199)
        self.assertEqual(len(r.records), 6)
        self.assertEqual(r.current_index, 5)

    def test_validations(self):
        for club, token in ((True, 1), (-1, 1), (1, True), (1, -1)):
            with self.assertRaises(OriginalTeamSelectHumanRegistryError):
                OriginalRegisteredHumanRegistry().register(club, token)
        for flag in (True, -1, 2):
            with self.assertRaises(OriginalTeamSelectHumanRegistryError):
                OriginalRegisteredHumanRegistry(user_list_payload_deletion_flag=flag)
        with self.assertRaises(OriginalTeamSelectHumanRegistryError):
            OriginalRegisteredHumanRegistry(current_index=4)


if __name__ == "__main__":
    unittest.main()
