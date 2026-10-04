"""Source-closed numeric AudioHooks route for accepted first-screen Button presses.

The canonical Button@ease_2001 press handler at 0x64F7A0 calls the control's
numeric AudioHooks selector before changing button state. For the six already
source-verified PStartMenu/TeamSelect action buttons, constructor argument 4 is
the caption source pointer stored at Button +0x34, so it is present in the
verified first-screen resource path.

For an enabled source-accepted press in native animation group 0 or 1, slot 0
therefore returns numeric event 10. The handler sends state 0 and third argument
0x40. The recovered AudioHooks dispatcher routes (10, 0) to menus.bnk slot 2.

No human-readable meaning is assigned to event 10 or sample slot 2 here.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_audiohooks_menu_dispatch import menus_sample_for_audiohooks_event
from gate14_audiohooks_menu_playback import (
    MenuPcmPlaybackBackend,
    MenuPcmPlaybackSummary,
    play_audiohooks_menu_pcm,
)


class Gate14FirstScreenButtonAudioError(ValueError):
    pass


BUTTON_TEXT_CONSTRUCTOR_VA = 0x652FD0
BUTTON_TEXT_BASE_CONSTRUCTOR_VA = 0x651E30
BUTTON_CAPTION_SOURCE_FIELD_OFFSET = 0x34
BUTTON_AUDIO_SELECTOR_VA = 0x6528A0
BUTTON_PRESS_HANDLER_VA = 0x64F7A0
BUTTON_PRESS_AUDIO_CALLSITE_VA = 0x64F7FE
BUTTON_POINTER_HANDLER_VA = 0x64FBE0
BUTTON_POINTER_ENTER_AUDIO_CALLSITE_VA = 0x64FC31
BUTTON_POINTER_LEAVE_AUDIO_CALLSITE_VA = 0x64FC91

PSTARTMENU_VTABLE_VA = 0x7C64E0
PSTARTMENU_OWNER_ACCEPT_SLOT_OFFSET = 0x0C
PSTARTMENU_OWNER_ACCEPT_VA = 0x42DE00
TEAMSELECT_VTABLE_VA = 0x7C7650
TEAMSELECT_OWNER_ACCEPT_SLOT_OFFSET = 0x0C
TEAMSELECT_OWNER_ACCEPT_VA = 0x5CFA50
OWNER_ACCEPT_RETURN_VALUE = 1

# 0x651E30 stores its fourth argument at +0x34. 0x652FD0 forwards all eleven
# arguments unchanged. These are the already recovered first-screen action
# button construction sites.
PSTARTMENU_ACTION_BUTTON_CALLS = (
    0x4C1C84,
    0x4C1CDF,
    0x4C1D3C,
    0x4C1D9A,
)
TEAMSELECT_ACTION_BUTTON_CALLS = (
    0x4D88BA,
    0x4D8921,
)
FIRST_SCREEN_ACTION_BUTTON_CALLS = (
    *PSTARTMENU_ACTION_BUTTON_CALLS,
    *TEAMSELECT_ACTION_BUTTON_CALLS,
)

# TeamSelect Back passes **0x98211C as argument 4. TeamSelect Start obtains
# **0x982124 through 0x4D9270 and passes that result as argument 4.
TEAMSELECT_BACK_CAPTION_GLOBAL_PTR_VA = 0x98211C
TEAMSELECT_START_CAPTION_GLOBAL_PTR_VA = 0x982124
TEAMSELECT_START_CAPTION_HELPER_VA = 0x4D9270

BUTTON_PRESS_STATE_VALUE = 0
BUTTON_PRESS_THIRD_ARGUMENT = 0x40
BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID = 10
BUTTON_CAPTION_ABSENT_EVENT_ID = 2
BUTTON_PRESS_MENU_SAMPLE_SLOT = 2
BUTTON_POINTER_ENTER_STATE_VALUE = 6
BUTTON_POINTER_LEAVE_STATE_VALUE = 7
BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT = 3


@dataclass(frozen=True)
class FirstScreenButtonAudioRoute:
    event_id: int
    state_value: int
    third_argument: int
    sample_slot: int
    caption_source_present: bool
    native_group: int
    semantic_event_binding_recovered: bool = False
    sample_meaning_recovered: bool = False
    front_end_binding_integrated: bool = False
    audible_windows_verified: bool = False

    def __post_init__(self) -> None:
        allowed_numeric_routes = {
            (2, BUTTON_PRESS_STATE_VALUE, BUTTON_PRESS_MENU_SAMPLE_SLOT),
            (10, BUTTON_PRESS_STATE_VALUE, BUTTON_PRESS_MENU_SAMPLE_SLOT),
            (
                10,
                BUTTON_POINTER_ENTER_STATE_VALUE,
                BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT,
            ),
        }
        if (self.event_id, self.state_value, self.sample_slot) not in allowed_numeric_routes:
            raise Gate14FirstScreenButtonAudioError(
                "first-screen Button route is not one of the source-closed numeric routes"
            )
        if self.third_argument != 0x40:
            raise Gate14FirstScreenButtonAudioError(
                "first-screen Button audio route must retain arg3 0x40"
            )
        if self.native_group not in (0, 1):
            raise Gate14FirstScreenButtonAudioError(
                "accepted enabled first-screen press must use native group 0 or 1"
            )
        if (
            self.semantic_event_binding_recovered
            or self.sample_meaning_recovered
            or self.front_end_binding_integrated
            or self.audible_windows_verified
        ):
            raise Gate14FirstScreenButtonAudioError(
                "numeric press route cannot promote semantic/integration/audibility claims"
            )


def source_accepted_button_press_route(
    *,
    caption_source_present: bool,
    native_group: int,
) -> FirstScreenButtonAudioRoute:
    """Return the original numeric AudioHooks route for one accepted enabled press.

    The generic handler rejects disabled group-2 controls before the AudioHooks
    call, so group 2 is deliberately not accepted here.
    """
    if type(caption_source_present) is not bool:
        raise Gate14FirstScreenButtonAudioError(
            "caption_source_present must be boolean"
        )
    if type(native_group) is not int or native_group not in (0, 1):
        raise Gate14FirstScreenButtonAudioError(
            "accepted enabled press requires native group 0 or 1"
        )

    event_id = (
        BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID
        if caption_source_present
        else BUTTON_CAPTION_ABSENT_EVENT_ID
    )
    dispatch = menus_sample_for_audiohooks_event(
        event_id,
        BUTTON_PRESS_STATE_VALUE,
    )
    if dispatch.sample_slot != BUTTON_PRESS_MENU_SAMPLE_SLOT:
        raise Gate14FirstScreenButtonAudioError(
            "source AudioHooks dispatch drifted from first-screen press route"
        )
    return FirstScreenButtonAudioRoute(
        event_id=event_id,
        state_value=BUTTON_PRESS_STATE_VALUE,
        third_argument=BUTTON_PRESS_THIRD_ARGUMENT,
        sample_slot=dispatch.sample_slot,
        caption_source_present=caption_source_present,
        native_group=native_group,
    )


def verified_first_screen_action_press_route(
    native_group: int = 0,
) -> FirstScreenButtonAudioRoute:
    """Route any of the six verified captioned first-screen action buttons.

    Their constructor argument 4 is the caption source pointer retained at
    Button +0x34, so the verified path uses caption_source_present=True.
    """
    return source_accepted_button_press_route(
        caption_source_present=True,
        native_group=native_group,
    )


def verified_first_screen_pointer_enter_route(
    native_group: int = 0,
) -> FirstScreenButtonAudioRoute:
    """Return the numeric route sent when the proven pointer handler enters."""
    if type(native_group) is not int or native_group not in (0, 1):
        raise Gate14FirstScreenButtonAudioError(
            "accepted enabled pointer enter requires native group 0 or 1"
        )
    event_id = BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID
    dispatch = menus_sample_for_audiohooks_event(
        event_id,
        BUTTON_POINTER_ENTER_STATE_VALUE,
    )
    if dispatch.sample_slot != BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT:
        raise Gate14FirstScreenButtonAudioError(
            "source AudioHooks dispatch drifted from first-screen pointer-enter route"
        )
    return FirstScreenButtonAudioRoute(
        event_id=event_id,
        state_value=BUTTON_POINTER_ENTER_STATE_VALUE,
        third_argument=BUTTON_PRESS_THIRD_ARGUMENT,
        sample_slot=dispatch.sample_slot,
        caption_source_present=True,
        native_group=native_group,
    )


def verified_first_screen_pointer_leave_is_silent(
    native_group: int = 0,
) -> bool:
    """Prove the exact pointer-leave numeric route is silent for event 10."""
    if type(native_group) is not int or native_group not in (0, 1):
        raise Gate14FirstScreenButtonAudioError(
            "accepted enabled pointer leave requires native group 0 or 1"
        )
    dispatch = menus_sample_for_audiohooks_event(
        BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID,
        BUTTON_POINTER_LEAVE_STATE_VALUE,
    )
    return dispatch.sample_slot is None


def play_verified_first_screen_action_press(
    menus_bnk: bytes,
    backend: MenuPcmPlaybackBackend | None,
    *,
    native_group: int = 0,
) -> MenuPcmPlaybackSummary:
    """Deliver the verified numeric press route through the existing PCM bridge.

    This is an adapter for a source-accepted press. It is not itself a live
    PStartMenu/TeamSelect input binding and therefore cannot promote
    login_menu_audio_integrated or audible_windows_verified.
    """
    route = verified_first_screen_action_press_route(native_group)
    return play_audiohooks_menu_pcm(
        menus_bnk,
        route.event_id,
        route.state_value,
        backend,
    )


def first_screen_button_audio_contract() -> dict:
    return {
        "button_text_constructor_va": BUTTON_TEXT_CONSTRUCTOR_VA,
        "button_text_base_constructor_va": BUTTON_TEXT_BASE_CONSTRUCTOR_VA,
        "caption_source_field_offset": BUTTON_CAPTION_SOURCE_FIELD_OFFSET,
        "audio_selector_va": BUTTON_AUDIO_SELECTOR_VA,
        "press_handler_va": BUTTON_PRESS_HANDLER_VA,
        "press_audio_callsite_va": BUTTON_PRESS_AUDIO_CALLSITE_VA,
        "pointer_handler_va": BUTTON_POINTER_HANDLER_VA,
        "pointer_enter_audio_callsite_va": BUTTON_POINTER_ENTER_AUDIO_CALLSITE_VA,
        "pointer_leave_audio_callsite_va": BUTTON_POINTER_LEAVE_AUDIO_CALLSITE_VA,
        "pstartmenu_vtable_va": PSTARTMENU_VTABLE_VA,
        "pstartmenu_owner_accept_slot_offset": PSTARTMENU_OWNER_ACCEPT_SLOT_OFFSET,
        "pstartmenu_owner_accept_va": PSTARTMENU_OWNER_ACCEPT_VA,
        "teamselect_vtable_va": TEAMSELECT_VTABLE_VA,
        "teamselect_owner_accept_slot_offset": TEAMSELECT_OWNER_ACCEPT_SLOT_OFFSET,
        "teamselect_owner_accept_va": TEAMSELECT_OWNER_ACCEPT_VA,
        "owner_accept_return_value": OWNER_ACCEPT_RETURN_VALUE,
        "first_screen_owner_acceptance_recovered": True,
        "pstartmenu_action_button_calls": PSTARTMENU_ACTION_BUTTON_CALLS,
        "teamselect_action_button_calls": TEAMSELECT_ACTION_BUTTON_CALLS,
        "first_screen_action_button_count": len(FIRST_SCREEN_ACTION_BUTTON_CALLS),
        "teamselect_back_caption_global_ptr_va": (
            TEAMSELECT_BACK_CAPTION_GLOBAL_PTR_VA
        ),
        "teamselect_start_caption_global_ptr_va": (
            TEAMSELECT_START_CAPTION_GLOBAL_PTR_VA
        ),
        "teamselect_start_caption_helper_va": TEAMSELECT_START_CAPTION_HELPER_VA,
        "accepted_enabled_caption_button_event_id": (
            BUTTON_CAPTION_PRESENT_ENABLED_EVENT_ID
        ),
        "accepted_press_state_value": BUTTON_PRESS_STATE_VALUE,
        "accepted_press_third_argument": BUTTON_PRESS_THIRD_ARGUMENT,
        "menus_sample_slot": BUTTON_PRESS_MENU_SAMPLE_SLOT,
        "pointer_enter_state_value": BUTTON_POINTER_ENTER_STATE_VALUE,
        "pointer_enter_menus_sample_slot": BUTTON_POINTER_ENTER_MENU_SAMPLE_SLOT,
        "pointer_leave_state_value": BUTTON_POINTER_LEAVE_STATE_VALUE,
        "pointer_leave_is_silent": True,
        "semantic_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "front_end_binding_integrated": False,
        "audible_windows_verified": False,
        "gate14_complete": False,
    }
