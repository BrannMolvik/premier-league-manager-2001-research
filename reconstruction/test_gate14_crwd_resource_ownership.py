"""Tests for source-backed FM2001 CRWD resource selection."""
from dataclasses import replace
import unittest

from gate14_crwd_resource_ownership import (
    ACTIVE_BANK_HANDLE_GLOBAL_VA,
    ACTIVE_BANK_ID_GLOBAL_VA,
    ACTIVE_CARD_HANDLE_GLOBAL_VA,
    CMIDI,
    CMIDI_INIT_VA,
    CROWD_BANK,
    CROWD_CARD,
    CRWD_PAIR_INIT_VA,
    CRWD_PATH_FORMAT_VA,
    CRWD_RESOURCE_LOADER_VA,
    CRWD_RESOURCES,
    MAIN_AUDIO_INIT_VA,
    RUNTIME_MODE_GLOBAL_VA,
    TRAFF_BANK,
    TRAFF_CARD,
    Gate14CrwdResourceOwnershipError,
    crwd_selection_for_runtime_mode,
)


class Gate14CrwdResourceOwnershipTests(unittest.TestCase):
    def test_exact_source_resources_and_addresses(self):
        self.assertEqual(MAIN_AUDIO_INIT_VA, 0x6D0AC0)
        self.assertEqual(CMIDI_INIT_VA, 0x7229B0)
        self.assertEqual(CRWD_RESOURCE_LOADER_VA, 0x722A80)
        self.assertEqual(CRWD_PAIR_INIT_VA, 0x722AF0)
        self.assertEqual(CRWD_PATH_FORMAT_VA, 0x866268)
        self.assertEqual(RUNTIME_MODE_GLOBAL_VA, 0xAD62A0)
        self.assertEqual(ACTIVE_BANK_HANDLE_GLOBAL_VA, 0xA87850)
        self.assertEqual(ACTIVE_CARD_HANDLE_GLOBAL_VA, 0xA87854)
        self.assertEqual(ACTIVE_BANK_ID_GLOBAL_VA, 0xA87858)

        self.assertEqual(
            [(item.filename, item.size_bytes) for item in CRWD_RESOURCES],
            [
                ("CMIDI.BNK", 446548),
                ("CROWD.BNK", 72592),
                ("CROWD.CRD", 5480),
                ("traff.bnk", 235952),
                ("TRAFF.CRD", 1384),
            ],
        )

    def test_runtime_mode_one_selects_traff_pair_without_cmidi(self):
        selection = crwd_selection_for_runtime_mode(1)
        self.assertIs(selection.bank, TRAFF_BANK)
        self.assertIs(selection.card, TRAFF_CARD)
        self.assertFalse(selection.initializes_cmidi)
        self.assertFalse(selection.exact_mode_semantics_recovered)

    def test_other_runtime_modes_select_crowd_pair_and_cmidi(self):
        for mode in (0, 2, -1, 99):
            with self.subTest(mode=mode):
                selection = crwd_selection_for_runtime_mode(mode)
                self.assertIs(selection.bank, CROWD_BANK)
                self.assertIs(selection.card, CROWD_CARD)
                self.assertTrue(selection.initializes_cmidi)
                self.assertFalse(selection.exact_mode_semantics_recovered)

    def test_resource_ownership_does_not_promote_audio_semantics(self):
        for item in CRWD_RESOURCES:
            with self.subTest(resource=item.filename):
                self.assertFalse(item.user_role_recovered)
                self.assertFalse(item.sample_mapping_recovered)
                self.assertFalse(item.playback_timing_recovered)
                self.assertFalse(item.music_semantics_recovered)
                for field in (
                    "user_role_recovered",
                    "sample_mapping_recovered",
                    "playback_timing_recovered",
                    "music_semantics_recovered",
                ):
                    with self.assertRaisesRegex(
                        Gate14CrwdResourceOwnershipError,
                        "cannot promote",
                    ):
                        replace(item, **{field: True})

    def test_numeric_mode_cannot_be_given_unrecovered_semantics(self):
        selection = crwd_selection_for_runtime_mode(0)
        with self.assertRaisesRegex(
            Gate14CrwdResourceOwnershipError,
            "cannot be given unrecovered",
        ):
            replace(selection, exact_mode_semantics_recovered=True)


if __name__ == "__main__":
    unittest.main()
