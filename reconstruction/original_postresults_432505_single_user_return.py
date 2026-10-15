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
    original_4290f0_eax_at_43254c: int,
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
    if (type(original_4290f0_eax_at_43254c) is not int or
        type(original_516010_al_at_432559) is not int or
        original_4290f0_eax_at_43254c not in (0,1) or
        not 0<=original_516010_al_at_432559<=0xff):
        raise OriginalPostResultsReturnSourceError(
            "source 4290F0 full EAX is exactly 0/1 and 516010 AL must be byte")
    if (type(original_registered_manager_count_8755e4) is not int or
        original_registered_manager_count_8755e4!=1):
        raise OriginalPostResultsReturnSourceError(
            "only original one-registered-manager 4325DF path is source-qualified")
    if (original_875680_settings_owner_pointer!=0 or
        original_4290f0_eax_at_43254c==0 or
        original_516010_al_at_432559==0):
        raise OriginalPostResultsReturnSourceError(
            "original 4325DF PStartMenu branch native guards not met")
    return SourceOriginalSingleUserStartMenuReturn(
        original_global_date_9847fc,
        original_reached_user_pointer_4139d0,
        original_registered_manager_count_8755e4,
    )


@dataclass(frozen=True)
class SourceOriginal4290F0Return:
    """Native 4290F0's actual final EAX predicate, not its side effects."""
    original_global_87755a_byte: int
    original_user_10d8_first_read: int | None
    original_user_10d8_after_callbacks: int | None
    original_4290f0_eax_result: int
    original_4290f0_exit_va: int
    native_intervening_callbacks_executed: bool = False
    original_gui_side_effects_proven: bool = False


def source_original_4290f0_return_from_reached(
    *,
    original_global_87755a_byte_at_5160a0: int,
    original_current_user_record_at_429126: bytes | None,
    original_current_user_record_at_429424: bytes | None,
) -> SourceOriginal4290F0Return:
    """Read original 5160A0 early exit or BOTH reached +10D8 reads.

    Original 4290F0 calls 5160A0 (global 87755A byte).
    If nonzero, it returns full EAX=0 without touching the user+10D8.
    If zero, it checks user+10D8 at 429126 and may execute mutable
    callbacks selected by its value 1..5, finally reading user+10D8
    again at 429424 and returns SETNE AL. A pre-call field alone
    cannot be assumed unchanged by those callbacks.
    """
    from struct import unpack_from
    flag=original_global_87755a_byte_at_5160a0
    if type(flag) is not int or not 0<=flag<=0xff:
        raise OriginalPostResultsReturnSourceError("source 87755A BYTE required")
    first=original_current_user_record_at_429126
    after=original_current_user_record_at_429424
    if flag:
        if first is not None or after is not None:
            raise OriginalPostResultsReturnSourceError(
                "original 5160A0 early exit must not read user+10D8")
        return SourceOriginal4290F0Return(flag,None,None,0,0x429125)
    if (type(first) is not bytes or len(first)<0x10dc or
        type(after) is not bytes or len(after)<0x10dc):
        raise OriginalPostResultsReturnSourceError(
            "actual native user+10D8 bytes before and after reached callbacks required")
    old=unpack_from("<I",first,0x10d8)[0]
    final=unpack_from("<I",after,0x10d8)[0]
    return SourceOriginal4290F0Return(flag,old,final,
         int(final!=0),0x429441)


def source_original_432505_single_user_startmenu_from_4290f0(
    *, source_4290f0: SourceOriginal4290F0Return,
    **original_432505_source_inputs,
) -> SourceOriginalSingleUserStartMenuReturn:
    if type(source_4290f0) is not SourceOriginal4290F0Return:
        raise OriginalPostResultsReturnSourceError(
            "native 4290F0 return must be source-joined by its original producer")
    if "original_4290f0_eax_at_43254c" in original_432505_source_inputs:
        raise OriginalPostResultsReturnSourceError(
            "cannot override source-qualified 4290F0 predicate")
    return source_original_432505_single_user_startmenu_plan(
        original_4290f0_eax_at_43254c=source_4290f0.original_4290f0_eax_result,
        **original_432505_source_inputs)
