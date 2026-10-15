"""Source-only original 5DA987–5DAA0B nonzero-coefficient D88 world branch.

Original private EXE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Requires existing 5DA981 verified *nonzero* match coefficient branch,
actual 5E43B0→5E48D0 returned QWORD, actual native 4037B0 human
predicate at 5DA9B3 and 403850 selected first-side +694 owner twice.
Human path stores second fetched DWORD [+694]+0xC to match context+D88,
and FILD signed first +0xC minus converted result to stack+0x30.
AI/nonhuman path invokes 668350 truncation on 5E48D0 QWORD,
stores its low DWORD to D88 and clears stack+0x30 QWORD.
No original native callbacks or GameState are executed.
"""
from dataclasses import dataclass
from struct import unpack_from,pack_into
from original_native_5da967_coeff_guard import SourceOriginal5DA967CoefficientGuardReceipt
from original_native_5db389_component_inputs import _native_668350_low32


class Original5DA9B1D88SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5DA9B1D88Receipt:
    original_first_side_pointer: int
    original_5da9b3_full_key_registered_human: bool
    original_context_after_d88: bytes
    original_stack_30_qword_after_branch: bytes
    original_user694_first_read_dword_if_human: int | None
    original_user694_second_read_dword_if_human: int | None
    original_5e43b0_executed: bool = False
    original_5e48d0_executed: bool = False
    original_4037b0_403850_executed: bool = False
    original_game_state_updated: bool = False


def _ptr(value,name):
    if type(value) is not int or not 0<value<=0xffffffff:
        raise Original5DA9B1D88SourceError(name+" original reached pointer required")
    return value


def source_original_5da9b1_match_d88_stage(
    *, original_coefficients_at_5da981: SourceOriginal5DA967CoefficientGuardReceipt,
    original_5da9a8_5e48d0_return_qword: bytes,
    original_5da987_match_processing_context_pointer: int,
    original_processing_context_before_d88: bytes,
    original_5da9b3_first_side_club_pointer: int,
    original_5da9b3_4037b0_human_result: bool,
    original_5da9be_403850_selected_user_pointer_if_human: int | None,
    original_5da9d6_403850_selected_user_pointer_if_human: int | None,
    original_5da9c3_selected_user694_pointer_first_if_human: int | None,
    original_5da9db_selected_user694_pointer_second_if_human: int | None,
    original_reached_694_first_record_if_human: bytes | None,
    original_reached_694_second_record_if_human: bytes | None,
    original_reached_x87_stack30_fstp_qword_if_human: bytes | None,
) -> SourceOriginal5DA9B1D88Receipt:
    source=original_coefficients_at_5da981
    if type(source) is not SourceOriginal5DA967CoefficientGuardReceipt or source.original_5da981_taken_zero_branch_to_5dac05:
        raise Original5DA9B1D88SourceError("native 5DA981 zero branch bypasses entire 5DA987 D88 stage")
    first=_ptr(original_5da9b3_first_side_club_pointer,"5DA9B3 club")
    if first!=source.original_first_side_club_pointer:
        raise Original5DA9B1D88SourceError("native 5DA9B3 ECX club differs from coefficient first side")
    _ptr(original_5da987_match_processing_context_pointer,"match processor")
    context=original_processing_context_before_d88
    if type(context) is not bytes or len(context)<0xd8c:
        raise Original5DA9B1D88SourceError("actual original processing context bytes through D88 required")
    converted=original_5da9a8_5e48d0_return_qword
    if type(converted) is not bytes or len(converted)!=8:
        raise Original5DA9B1D88SourceError("actual source 5E48D0 FSTP QWORD required")
    human=original_5da9b3_4037b0_human_result
    if type(human) is not bool:
        raise Original5DA9B1D88SourceError("actual original 4037B0 result at 5DA9B3 required")
    args=(original_5da9be_403850_selected_user_pointer_if_human,
        original_5da9d6_403850_selected_user_pointer_if_human,
        original_5da9c3_selected_user694_pointer_first_if_human,
        original_5da9db_selected_user694_pointer_second_if_human,
        original_reached_694_first_record_if_human,
        original_reached_694_second_record_if_human,
        original_reached_x87_stack30_fstp_qword_if_human)
    first_dword=second_dword=None
    if human:
        p,q,pp,qq=(_ptr(v,n) for v,n in zip(args[:4],
            ("first 403850 user","second 403850 user","first +694","second +694")))
        if p!=q or pp!=qq:
            raise Original5DA9B1D88SourceError("native repeated 403850 selected human or +694 owner changed")
        a,b,delta=args[4:]
        if (type(a) is not bytes or len(a)<0x10 or
            type(b) is not bytes or len(b)<0x10 or
            type(delta) is not bytes or len(delta)!=8):
            raise Original5DA9B1D88SourceError("source+694 two DWORD+C snapshots and FSTP QWORD required")
        first_dword=unpack_from("<I",a,0xc)[0]
        second_dword=unpack_from("<I",b,0xc)[0]
        # The original reads and subtracts the FIRST signed value,
        # but D88 receives the SECOND raw value. No fabricated x87
        # delta is constructed from portable double arithmetic.
        stored=second_dword
        stack30=delta
    else:
        if any(item is not None for item in args):
            raise Original5DA9B1D88SourceError("nonhuman source 5DA9EC must not use human +694")
        try:
            stored=_native_668350_low32(converted,"5DA9EC AI source")
        except ValueError as exc:
            raise Original5DA9B1D88SourceError("unqualified original nonhuman FPU conversion") from exc
        stack30=bytes(8)
    after=bytearray(context)
    pack_into("<I",after,0xd88,stored)
    return SourceOriginal5DA9B1D88Receipt(
        first,human,bytes(after),stack30,first_dword,second_dword)
