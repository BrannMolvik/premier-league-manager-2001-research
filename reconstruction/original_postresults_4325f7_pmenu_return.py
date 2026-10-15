"""Original 4325F7 -> 432614/43261F distinct PMenu return routes.

Reopened canonical original PE 833bf95e..b7cc3. 4325F7 tests
native post-NEXT local byte [ESP+12]. If zero, the source optionally
calls 4A9E20 when settings 875680 is null, resets 8755D4=0,
and calls 4C2FB0(1,0,1) to reconstruct PMenu.

If [ESP+12]!=0, native 43261F checks local DWORD [ESP+14]==2;
only then does 432626–432639 increment selected human ordinal,
signed IDIV by registered-user count 8755E4 and store signed
remainder into 8755D4, release possible active 876760 menu
stack and call 4C2FB0(1,1,1). When state!=2 it RETs with
no active-player advance or PMenu construction.

The preceding 432505/43256A callbacks choose when these
branches are reached. Supply the exact reached original branch
and native locals; this plan never invents 4290F0/516010 outcome,
native cleanup callbacks, GameState user switching or a GUI return.
"""
from dataclasses import dataclass

class OriginalPBgReturnSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalPBgPMenuReturn:
    original_return_branch: int
    original_native_selected_manager_8755d4_after: int | None
    original_source_pmenu_args: tuple[int,int,int] | None
    original_4a9e20_cleanup_reached: bool
    original_active_876760_disposal_may_be_reached: bool
    original_needs_real_native_lifecycle: bool = True
    native_callbacks_executed: bool = False
    game_state_mutated: bool = False
    original_gui_return_verified: bool = False


def source_original_4325f7_pmenu_return(
    *,
    original_4325f7_source_reached: bool,
    original_local_byte_esp12: int,
    original_local_dword_esp14: int | None,
    original_875680_settings_owner_pointer: int,
    original_8755d4_current_registered_ordinal: int | None,
    original_8755e4_registered_user_count: int | None,
) -> SourceOriginalPBgPMenuReturn:
    if type(original_4325f7_source_reached) is not bool or not original_4325f7_source_reached:
        raise OriginalPBgReturnSourceError("native 4325F7 source reachability required")
    if type(original_local_byte_esp12) is not int or not 0<=original_local_byte_esp12<=255:
        raise OriginalPBgReturnSourceError("source [ESP+12] byte required")
    if (type(original_875680_settings_owner_pointer) is not int or
        not 0<=original_875680_settings_owner_pointer<=0xffffffff):
        raise OriginalPBgReturnSourceError("source settings owner pointer required")
    if original_local_byte_esp12==0:
        if (original_local_dword_esp14 is not None or
            original_8755d4_current_registered_ordinal is not None or
            original_8755e4_registered_user_count is not None):
            raise OriginalPBgReturnSourceError("bypassed native rotation fields must be absent")
        return SourceOriginalPBgPMenuReturn(
            0x4325F7,0,(1,0,1),
            original_875680_settings_owner_pointer==0,False)
    if type(original_local_dword_esp14) is not int or not 0<=original_local_dword_esp14<=0xffffffff:
        raise OriginalPBgReturnSourceError("reached 43261F source state DWORD required")
    if original_local_dword_esp14!=2:
        if original_8755d4_current_registered_ordinal is not None or original_8755e4_registered_user_count is not None:
            raise OriginalPBgReturnSourceError("rotation skipped; native manager fields unvisited")
        return SourceOriginalPBgPMenuReturn(0x43261F,None,None,False,False)
    old=original_8755d4_current_registered_ordinal
    count=original_8755e4_registered_user_count
    if (type(old) is not int or type(count) is not int
            or not 0<=old<=0x7ffffffe or not 1<=count<=0x7fffffff
            or old>=count):
        raise OriginalPBgReturnSourceError(
            "native signed manager ordinal/count needed for safe IDIV 43262D")
    # For reached nonnegative, bounded source domain, CDQ/IDIV
    # matches Python remainder. Negative/overflow original paths remain
    # unqualified instead of falsely claiming C integer behavior.
    return SourceOriginalPBgPMenuReturn(0x43261F,(old+1)%count,(1,1,1),False,True)
