"""Tests for the source-closed first-screen numeric Button audio route."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from gate14_audiohooks_menu_playback import MenuPcmPlaybackSummary
from gate14_first_screen_button_audio import (
    BUTTON_AUDIO_SELECTOR_VA,
    BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID,
    BUTTON_CAPTION_SOURCE_FIELD_OFFSET,
    BUTTON_PRESS_AUDIO_CALLSITE_VA,
    BUTTON_PRESS_HANDLER_VA,
    BUTTON_PRESS_MENU_SAMPLE_SLOT,
    BUTTON_PRESS_STATE_VALUE,
    BUTTON_PRESS_THIRD_ARGUMENT,
    BUTTON_POINTER_ENTER_AUDIO_CALLSITE_VA,
    BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT,
    BUTTON_POINTER_ENTER_STATE_VALUE,
    BUTTON_POINTER_HANDLER_VA,
    BUTTON_POINTER_LEAVE_AUDIO_CALLSITE_VA,
    BUTTON_POINTER_LEAVE_STATE_VALUE,
    BUTTON_TEXT_BASE_CONSTRUCTOR_VA,
    BUTTON_TEXT_CONSTRUCTOR_VA,
    FIRST_SCREEN_ACTION_BUTTON_CALLS,
    PSTARTMENU_ACTION_BUTTON_CALLS,
    PSTARTMENU_OWNER_ACCEPT_SLOT_OFFSET,
    PSTARTMENU_OWNER_ACCEPT_VA,
    PSTARTMENU_VTABLE_VA,
    TEAMSELECT_ACTION_BUTTON_CALLS,
    TEAMSELECT_OWNER_ACCEPT_SLOT_OFFSET,
    TEAMSELECT_OWNER_ACCEPT_VA,
    TEAMSELECT_VTABLE_VA,
    OWNER_ACCEPT_RETURN_VALUE,
    TEAMSELECT_BACK_CAPTION_GLOBAL_PTR_VA,
    TEAMSELECT_START_CAPTION_GLOBAL_PTR_VA,
    TEAMSELECT_START_CAPTION_HELPER_VA,
    FirstScreenButtonAudioRoute,
    Gate14FirstScreenButtonAudioError,
    first_screen_button_audio_contract,
    play_verified_first_screen_action_press,
    source_accepted_button_press_route,
    verified_first_screen_action_press_route,
    verified_first_screen_pointer_enter_route,
    verified_first_screen_pointer_leave_is_silent,
)


class Gate14FirstScreenButtonAudioTests(unittest.TestCase):
    def test_exact_source_anchors_and_six_action_button_constructors(self):
        self.assertEqual(BUTTON_TEXT_CONSTRUCTOR_VA, 0x652FD0)
        self.assertEqual(BUTTON_TEXT_BASE_CONSTRUCTOR_VA, 0x651E30)
        self.assertEqual(BUTTON_CAPTION_SOURCE_FIELD_OFFSET, 0x34)
        self.assertEqual(BUTTON_AUDIO_SELECTOR_VA, 0x6528A0)
        self.assertEqual(BUTTON_PRESS_HANDLER_VA, 0x64F7A0)
        self.assertEqual(BUTTON_PRESS_AUDIO_CALLSITE_VA, 0x64F7FE)
        self.assertEqual(BUTTON_POINTER_HANDLER_VA, 0x64FBE0)
        self.assertEqual(BUTTON_POINTER_ENTER_AUDIO_CALLSITE_VA, 0x64FC31)
        self.assertEqual(BUTTON_POINTER_LEAVE_AUDIO_CALLSITE_VA, 0x64FC91)
        self.assertEqual(
            PSTARTMENU_ACTION_BUTTON_CALLS,
            (0x4C1C84, 0x4C1CDF, 0x4C1D3C, 0x4C1D9A),
        )
        self.assertEqual(
            TEAMSELECT_ACTION_BUTTON_CALLS,
            (0x4D88BA, 0x4D8921),
        )
        self.assertEqual(len(FIRST_SCREEN_ACTION_BUTTON_CALLS), 6)
        self.assertEqual(len(set(FIRST_SCREEN_ACTION_BUTTON_CALLS)), 6)
        self.assertEqual(TEAMSELECT_BACK_CAPTION_GLOBAL_PTR_VA, 0x98211C)
        self.assertEqual(TEAMSELECT_START_CAPTION_GLOBAL_PTR_VA, 0x982124)
        self.assertEqual(TEAMSELECT_START_CAPTION_HELPER_VA, 0x4D9270)
        self.assertEqual(PSTARTMENU_VTABLE_VA, 0x7C64E0)
        self.assertEqual(PSTARTMENU_OWNER_ACCEPT_SLOT_OFFSET, 0x0C)
        self.assertEqual(PSTARTMENU_OWNER_ACCEPT_VA, 0x42DE00)
        self.assertEqual(TEAMSELECT_VTABLE_VA, 0x7C7650)
        self.assertEqual(TEAMSELECT_OWNER_ACCEPT_SLOT_OFFSET, 0x0C)
        self.assertEqual(TEAMSELECT_OWNER_ACCEPT_VA, 0x5CFA50)
        self.assertEqual(OWNER_ACCEPT_RETURN_VALUE, 1)

    def test_verified_captioned_enabled_press_is_event10_state0_arg40_slot2(self):
        for group in (0, 1):
            with self.subTest(group=group):
                route = verified_first_screen_action_press_route(group)
                self.assertEqual(
                    (
                        route.event_id,
                        route.state_value,
                        route.third_argument,
                        route.sample_slot,
                    ),
                    (10, 0, 0x40, 2),
                )
                self.assertTrue(route.caption_source_present)
                self.assertFalse(route.semantic_event_binding_recovered)
                self.assertFalse(route.sample_meaning_recovered)
                self.assertFalse(route.front_end_binding_integrated)
                self.assertFalse(route.audible_windows_verified)

    def test_pointer_enter_is_event10_state6_slot3_and_leave_is_silent(self):
        for group in (0, 1):
            with self.subTest(group=group):
                route = verified_first_screen_pointer_enter_route(group)
                self.assertEqual(
                    (
                        route.event_id,
                        route.state_value,
                        route.third_argument,
                        route.sample_slot,
                    ),
                    (10, 6, 0x40, 3),
                )
                self.assertTrue(
                    verified_first_screen_pointer_leave_is_silent(group)
                )

    def test_caption_absent_selector_branch_remains_numeric_event2(self):
        route = source_accepted_button_press_route(
            caption_source_present=False,
            native_group=0,
        )
        self.assertEqual(route.event_id, 2)
        self.assertEqual(route.sample_slot, 2)

    def test_disabled_group2_cannot_be_promoted_to_press_audio(self):
        with self.assertRaisesRegex(
            Gate14FirstScreenButtonAudioError,
            "group 0 or 1",
        ):
            verified_first_screen_action_press_route(2)

    def test_route_record_rejects_semantic_or_integration_promotion(self):
        route = verified_first_screen_action_press_route()
        for field in (
            "semantic_event_binding_recovered",
            "sample_meaning_recovered",
            "front_end_binding_integrated",
            "audible_windows_verified",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14FirstScreenButtonAudioError,
                    "cannot promote",
                ):
                    replace(route, **{field: True})

    def test_playback_adapter_uses_only_event10_state0_numeric_route(self):
        expected = MenuPcmPlaybackSummary(
            event_id=10,
            state_value=0,
            sample_slot=2,
            backend_invoked=True,
            adapter_delivery_completed=True,
        )
        with patch(
            "gate14_first_screen_button_audio.play_audiohooks_menu_pcm",
            return_value=expected,
        ) as play:
            actual = play_verified_first_screen_action_press(
                b"bank",
                object(),
                native_group=1,
            )
        self.assertIs(actual, expected)
        play.assert_called_once_with(b"bank", 10, 0, unittest.mock.ANY)

    def test_contract_keeps_meaning_live_binding_and_audibility_false(self):
        contract = first_screen_button_audio_contract()
        self.assertEqual(
            contract["accepted_enabled_caption_button_event_id"],
            BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID,
        )
        self.assertEqual(
            contract["accepted_press_state_value"],
            BUTTON_PRESS_STATE_VALUE,
        )
        self.assertEqual(
            contract["accepted_press_third_argument"],
            BUTTON_PRESS_THIRD_ARGUMENT,
        )
        self.assertEqual(
            contract["menus_sample_slot"],
            BUTTON_PRESS_MENU_SAMPLE_SLOT,
        )
        self.assertTrue(contract["first_screen_owner_acceptance_recovered"])
        self.assertEqual(contract["owner_accept_return_value"], 1)
        self.assertEqual(
            contract["pointer_enter_state_value"],
            BUTTON_POINTER_ENTER_STATE_VALUE,
        )
        self.assertEqual(
            contract["pointer_enter_menus_sample_slot"],
            BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT,
        )
        self.assertEqual(
            contract["pointer_leave_state_value"],
            BUTTON_POINTER_LEAVE_STATE_VALUE,
        )
        self.assertTrue(contract["pointer_leave_is_silent"])
        self.assertFalse(contract["semantic_event_binding_recovered"])
        self.assertFalse(contract["sample_meaning_recovered"])
        self.assertFalse(contract["front_end_binding_integrated"])
        self.assertFalse(contract["audible_windows_verified"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
