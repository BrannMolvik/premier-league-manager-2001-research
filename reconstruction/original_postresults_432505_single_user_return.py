"""Source-bounded PBg 432505 -> 4325DF single-user PStartMenu exit.

Only ONE post-results branch is proven here. Source 432505 first performs
date formatting 64CCD0/64CE30 and active-user UI update 413AC0.
Then with settings owner 875680 NULL, selected user's 4290F0 nonzero,
global 516010 byte from 82856E true and original registered-user count
8755E4 <= 1, 4325DF clears 875614 and CALLS 4C3280 to enter PStartMenu.

The caller supplies actual reached original predicate results. No source
of those effects exists yet in normal portable GameState, and no other
PBg return paths are silently folded into this one.
"""
from dataclasses import dataclass


class OriginalPostResultsReturnSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalSingleUserStartMenuReturn:
    original_global_date_at_432505: int
    original_current_user_pointer_from_4139d0: int
    original_registered_user_count_8755e4: int
    original_reached_432505: bool = True
    original_branch_destination: int = 0x4325DF
    original_875614_zero_store_va: int = 0x4325DF
    original_start_menu_constructor_va: int = 0x4C3280
    original_413ac0_ui_update_execution_proven: bool = False
    original_4290f0_callback_execution_proven: bool = False
    live_game_state_modified: bool = False
    native_original_process_executed: bool = False
    windows11_gui_accepted: bool = False


def source_original_432505_single_user_startmenu_plan(
    *,
    original_reached_post_presults_432505: bool,
    original_global_date_9847fc: int,
    original_reached_user_pointer_4139d0: int,
    original_875680_settings_owner_pointer: int,
    original_4290f0_al_at_43254c: int,
    original_516010_al_at_432559: int,
    original_registered_manager_count_8755e4: int,
    original_413ac0_update_completed: bool,
) -> SourceOriginalSingleUserStartMenuReturn:
    if (type(original_reached_post_presults_432505) is not bool or
        not original_reached_post_presults_432505 or
        type(original_413ac0_update_completed) is not bool or
        not original_413ac0_update_completed):
        raise OriginalPostResultsReturnSourceError(
            "actual reached 432505 and completed 413AC0 update required")
    for name,value in (
        ("global date",original_global_date_9847fc),
        ("reached registered user",original_reached_user_pointer_4139d0),
        ("settings owner",original_875680_settings_owner_pointer),
    ):
        if type(value) is not int or not 0<=value<=0xffffffff:
            raise OriginalPostResultsReturnSourceError(
                "actual original "+name+" DWORD required")
    if not original_reached_user_pointer_4139d0:
        raise OriginalPostResultsReturnSourceError("native 4139D0 selected user cannot be null")
    if (type(original_4290f0_al_at_43254c) is not int or
        type(original_516010_al_at_432559) is not int or
        not 0<=original_4290f0_al_at_43254c<=0xff or
        not 0<=original_516010_al_at_432559<=0xff):
        raise OriginalPostResultsReturnSourceError(
            "actual native source 4290F0 and 516010 return bytes required")
    if (type(original_registered_manager_count_8755e4) is not int or
        original_registered_manager_count_8755e4!=1):
        raise OriginalPostResultsReturnSourceError(
            "only original one-registered-manager 4325DF path is source-qualified")
    if (original_875680_settings_owner_pointer!=0 or
        original_4290f0_al_at_43254c==0 or
        original_516010_al_at_432559==0):
        raise OriginalPostResultsReturnSourceError(
            "original 4325DF PStartMenu branch native guards not met")
    return SourceOriginalSingleUserStartMenuReturn(
        original_global_date_9847fc,
        original_reached_user_pointer_4139d0,
        original_registered_manager_count_8755e4,
    )
