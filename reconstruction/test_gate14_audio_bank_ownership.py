"""Tests for source-backed Gate-14 audio bank ownership."""
from dataclasses import replace
import unittest

from gate14_audio_bank_ownership import (
    ADVICE_LOADER_VA,
    ADVICE_PLAYBACK_VA,
    AUDIO_HOOKS_DISPATCH_VA,
    AUDIO_HOOKS_RTTI,
    AUDIO_HOOKS_VTABLE_VA,
    AUDIO_INIT_MENUS_GAME_VA,
    BANKS,
    BANK_HANDLE_BASE_VA,
    BANK_ID_BASE_VA,
    BANK_LOADER_VA,
    BANK_SLOT_STRIDE,
    GENERIC_AUDIO_CALLBACK_INSTALLER_VA,
    GENERIC_AUDIO_CALLBACK_REGISTRATION_VA,
    GENERIC_SFX_CALLBACK_VA,
    GENERIC_SFX_WRAPPER_VA,
    MAIN_AUDIO_BANK_INIT_VA,
    MENUS_PLAYBACK_VA,
    PLAYER_CALLS_LOADER_VA,
    Gate14AudioBankOwnershipError,
    advice_bank,
    audio_hooks_bank,
    bank_for_slot,
    generic_sfx_bank_for_type,
)


class Gate14AudioBankOwnershipTests(unittest.TestCase):
    def test_exact_slot_loading_contract(self):
        self.assertEqual(BANK_LOADER_VA, 0x6D01F0)
        self.assertEqual(AUDIO_INIT_MENUS_GAME_VA, 0x6D0160)
        self.assertEqual(PLAYER_CALLS_LOADER_VA, 0x6D0250)
        self.assertEqual(ADVICE_LOADER_VA, 0x6D02F0)
        self.assertEqual(MAIN_AUDIO_BANK_INIT_VA, 0x6D0AC0)

        self.assertEqual(
            [(item.slot, item.filename, item.string_va) for item in BANKS],
            [
                (0, "menus.bnk", 0x8611F0),
                (1, "game00.bnk", 0x8611E4),
                (2, "playercalls.bnk", 0x861214),
                (3, "Advice.bnk", 0x861224),
            ],
        )
        self.assertEqual(
            [item.handle_global_va for item in BANKS],
            [BANK_HANDLE_BASE_VA + index * BANK_SLOT_STRIDE for index in range(4)],
        )
        self.assertEqual(
            [item.bank_id_global_va for item in BANKS],
            [BANK_ID_BASE_VA + index * BANK_SLOT_STRIDE for index in range(4)],
        )

    def test_audio_hooks_dispatch_is_bound_to_menus_slot_only(self):
        bank = audio_hooks_bank()
        self.assertEqual(AUDIO_HOOKS_RTTI, ".?AVAudioHooks@@")
        self.assertEqual(AUDIO_HOOKS_VTABLE_VA, 0x7D73EC)
        self.assertEqual(AUDIO_HOOKS_DISPATCH_VA, 0x5DBFC0)
        self.assertEqual(bank.slot, 0)
        self.assertEqual(bank.filename, "menus.bnk")
        self.assertEqual(bank.playback_va, MENUS_PLAYBACK_VA)
        self.assertEqual(bank.playback_path, "AudioHooks event/sample dispatcher")

    def test_generic_callback_selects_game_and_playercalls_slots(self):
        self.assertEqual(GENERIC_SFX_WRAPPER_VA, 0x6D0030)
        self.assertEqual(GENERIC_SFX_CALLBACK_VA, 0x6D0050)
        self.assertEqual(GENERIC_AUDIO_CALLBACK_INSTALLER_VA, 0x6D0480)
        self.assertEqual(GENERIC_AUDIO_CALLBACK_REGISTRATION_VA, 0x7255A0)

        game = generic_sfx_bank_for_type(0)
        calls = generic_sfx_bank_for_type(1)
        self.assertEqual((game.slot, game.filename), (1, "game00.bnk"))
        self.assertEqual((calls.slot, calls.filename), (2, "playercalls.bnk"))
        self.assertIs(game.playback_va, GENERIC_SFX_CALLBACK_VA)
        self.assertIs(calls.playback_va, GENERIC_SFX_CALLBACK_VA)

        with self.assertRaisesRegex(
            Gate14AudioBankOwnershipError,
            "caller-supplied slot",
        ):
            generic_sfx_bank_for_type(2)

    def test_advice_bank_has_separate_direct_playback_helper(self):
        bank = advice_bank()
        self.assertEqual(bank.slot, 3)
        self.assertEqual(bank.filename, "Advice.bnk")
        self.assertEqual(bank.playback_va, ADVICE_PLAYBACK_VA)
        self.assertEqual(bank.playback_path, "direct Advice-bank playback helper")

    def test_no_bank_promotes_music_or_sample_semantics(self):
        for bank in BANKS:
            with self.subTest(bank=bank.filename):
                self.assertFalse(bank.role_semantics_recovered)
                self.assertFalse(bank.exact_sample_semantics_recovered)
                self.assertFalse(bank.music_semantics_recovered)
                for field in (
                    "role_semantics_recovered",
                    "exact_sample_semantics_recovered",
                    "music_semantics_recovered",
                ):
                    with self.assertRaisesRegex(
                        Gate14AudioBankOwnershipError,
                        "cannot promote",
                    ):
                        replace(bank, **{field: True})

    def test_unknown_slots_fail_closed(self):
        with self.assertRaisesRegex(Gate14AudioBankOwnershipError, "unknown"):
            bank_for_slot(4)
        with self.assertRaisesRegex(Gate14AudioBankOwnershipError, "uint8"):
            generic_sfx_bank_for_type(-1)


if __name__ == "__main__":
    unittest.main()
