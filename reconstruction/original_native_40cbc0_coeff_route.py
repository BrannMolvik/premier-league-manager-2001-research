"""Bounded original 5DA967->40CBC0 first-side coefficient route source.

Original PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Only chooses the original dispatch address. It DOES NOT execute native
4056D0/4056F0/4FA520, compute two output floating coefficients, run the
original match, or mutate GameState. No proprietary source binary attached.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original40CBC0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal40CBC0RouteReceipt:
    original_side_club_pointer: int
    original_club_14_raw_dword: int
    original_dispatch_table_selector: int | None
    original_selected_jump_target: int
    original_40cbc0_executed: bool = False
    original_coefficients_computed: bool = False
    live_game_state_updated: bool = False


# Source jump table 40CFA0 and byte selector table 40CFC0, 24..73 inclusive.
# Unlisted in-range selectors read 7, selecting native 40CF31 default.
_SPECIAL_NATIVE_JUMPS = {
    24: (0,0x40ce83),
    26: (1,0x40cbf2),
    31: (2,0x40ceda),
    33: (3,0x40ccc9),
    40: (4,0x40cd5d),
    66: (5,0x40ce09),
    73: (6,0x40cdb3),
}
_DEFAULT_NATIVE_TARGET = 0x40cf31


def source_original_5da967_40cbc0_club_coefficient_route(
    *,
    original_5da967_first_side_club_pointer: int,
    original_40cbc0_ecx_club_pointer: int,
    original_40cbc0_club_record: bytes,
) -> SourceOriginal40CBC0RouteReceipt:
    first=original_5da967_first_side_club_pointer
    passed=original_40cbc0_ecx_club_pointer
    if (type(first) is not int or type(passed) is not int or
        not 0<first<=0xffffffff or passed!=first):
        raise Original40CBC0SourceError("5DA967 first-side ECX source owner pointer mismatch")
    club=original_40cbc0_club_record
    if type(club) is not bytes or len(club)<0x18:
        raise Original40CBC0SourceError("actual original club record through +14 required")
    raw=unpack_from("<I",club,0x14)[0]
    if 24<=raw<=73:
        selector,target=_SPECIAL_NATIVE_JUMPS.get(raw,(7,_DEFAULT_NATIVE_TARGET))
    else:
        selector,target=None,_DEFAULT_NATIVE_TARGET
    return SourceOriginal40CBC0RouteReceipt(first,raw,selector,target)
