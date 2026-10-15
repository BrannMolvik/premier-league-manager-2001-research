"""Original 5DA8D9→5DA987 first-side coefficient stack and zero guard.

Source private original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.

Before 5DA967, 5DA93B..5DA963 clear current ESP+98 and +A0
as native QWORD doubles. At 5DA8D9/E0 before two pushes the
40CBC0 first/second output arguments become the *later* ESP+98/+A0.
5DA967 calls 40CBC0 using ESI native first-side ECX.
5DA96C compares second QWORD ESP+A0 to original 7BD5F8 0.0
via x87 FCOMP, and 5DA981 JE 5DAC05 on zero. This is source
projection only; no native match/memory/callback execute.
"""
from dataclasses import dataclass
from struct import unpack

from original_native_40cbc0_full_category_join import SourceOriginal40CBC0FullCategoryReceipt
from original_native_40cbc0_all_paths import (
    SourceOriginal40CBC0AllPathReceipt,source_original_40cbc0_all_dispatch_coefficients,
)

class Original5DA967CoefficientGuardError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal5DA967CoefficientGuardReceipt:
    original_first_side_club_pointer: int
    original_esp_at_5da967: int
    original_40cbc0_first_output_pointer: int
    original_40cbc0_second_output_pointer: int
    original_stack_98_qword_after: bytes
    original_stack_a0_qword_after: bytes
    original_5da981_taken_zero_branch_to_5dac05: bool
    source_native_calculation: SourceOriginal40CBC0AllPathReceipt
    original_5da2f0_executed: bool = False
    original_5da967_original_call_executed: bool = False
    live_game_state_updated: bool = False

def source_original_5da967_two_native_qwords_to_zero_guard(
    *, original_5da8e9_esi_first_side_club_pointer: int,
    original_source_first_side_category_receipt: SourceOriginal40CBC0FullCategoryReceipt,
    original_actual_categories_all_40cbc0_calls: tuple[int,...],
    original_esp_pointer_at_5da967: int,
    original_stack_98_qword_after_source_zero_initialization: bytes,
    original_stack_a0_qword_after_source_zero_initialization: bytes,
) -> SourceOriginal5DA967CoefficientGuardReceipt:
    p=original_5da8e9_esi_first_side_club_pointer
    esp=original_esp_pointer_at_5da967
    if (type(p) is not int or not 0<p<=0xffffffff or
            type(esp) is not int or not 0<esp<=0xffffffff-0xa8):
        raise Original5DA967CoefficientGuardError("original first-side ESI and ESP source addresses required")
    owner=original_source_first_side_category_receipt
    if (type(owner) is not SourceOriginal40CBC0FullCategoryReceipt or
        owner.source_first_side_route_and_category.first_side_dispatch.original_side_club_pointer!=p):
        raise Original5DA967CoefficientGuardError("original 40CBC0 ECX not same 5DA8E9 first-side ESI")
    first=original_stack_98_qword_after_source_zero_initialization
    second=original_stack_a0_qword_after_source_zero_initialization
    if first!=bytes(8) or second!=bytes(8):
        raise Original5DA967CoefficientGuardError("original 5DA93B..5DA963 zero-initialized QWORDs required")
    out=source_original_40cbc0_all_dispatch_coefficients(
        original_first_native_category_receipt=owner,
        original_actual_categories_for_each_4fa520_call=original_actual_categories_all_40cbc0_calls,
        original_ebp8_first_qword_pointer=esp+0x98,
        original_ebpc_second_qword_pointer=esp+0xa0,
        original_first_qword_before=first,
        original_second_qword_before=second)
    second_double=unpack('<d',out.original_second_qword_after)[0]
    # Reached finite IEEE754 literals are >= 0, and source original
    # 7BD5F8 is exact +0.0. Non-finite/negative results are not proven.
    if not (0.0<=second_double< float('inf')):
        raise Original5DA967CoefficientGuardError("unqualified original x87 FCOMP second QWORD")
    taken=second_double==0.0
    if taken != (not out.original_any_coefficient_written):
        raise Original5DA967CoefficientGuardError("original 5DA981 zero branch/store contradiction")
    return SourceOriginal5DA967CoefficientGuardReceipt(
        p,esp,esp+0x98,esp+0xa0,
        out.original_first_qword_after,out.original_second_qword_after,taken,out)
