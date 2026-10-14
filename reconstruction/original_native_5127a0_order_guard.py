"""Source-ordered per-side original 0x5127A0 match-world traversal.

This checks identity and causal ordering of explicitly reached native source
receipts. It does NOT run callbacks, trust fabricated event outputs, mutate
GameState, or imply native/world/playable parity.

Original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_419680_availability import Original419680AvailabilityReceipt


class Original5127A0OrderError(ValueError):
    pass


@dataclass(frozen=True)
class Original5127A0OrderedStep:
    """A source-observed step, not proof its original virtual ran here.

    Phase codes in original 5127A0 source order:
      return  = 419490 each whole-side roster player
      row     = 4197C0 each active row
      extra   = conditional 41A5B0 immediately after its row
      avail   = 419680 each whole-side roster player after all rows
    """
    phase: str
    original_player_id: int
    original_row_index: int | None = None
    original_row: Original5127A0RowCall | None = None
    original_availability: Original419680AvailabilityReceipt | None = None
    original_lookup_pointer_used: int | None = None


@dataclass(frozen=True)
class Original5127A0OrderedSide:
    pass_index: int
    source_roster_ids: tuple[int, ...]
    source_rows: tuple[Original5127A0RowCall, ...]
    original_615d10_lookup_pointer: int
    source_steps: tuple[Original5127A0OrderedStep, ...]


@dataclass(frozen=True)
class Original5127A0OrderReceipt:
    original_total_return_callbacks: int
    original_total_row_callbacks: int
    original_total_extra_callbacks: int
    original_total_availability_callbacks: int
    original_owner_passes: tuple[int, int]
    native_callbacks_executed: bool = False
    live_game_state_mutated: bool = False
    original_match_finished: bool = False


def _uint(value: int, bits: int, label: str) -> int:
    if type(value) is not int or not 0<=value<1<<bits:
        raise Original5127A0OrderError(f"source original {label} unsigned {bits}-bit required")
    return value


def _expected_steps(side: Original5127A0OrderedSide) -> tuple[tuple[str,int,int|None,Original5127A0RowCall|None], ...]:
    expected=[]
    for pid in side.source_roster_ids:
        expected.append(("return",pid,None,None))
    for i,row in enumerate(side.source_rows):
        expected.append(("row",row.source_player_pointer,i,row))
        if row.source_41a5b0_called_after_row:
            expected.append(("extra",row.source_player_pointer,i,row))
    for pid in side.source_roster_ids:
        expected.append(("avail",pid,None,None))
    return tuple(expected)


def source_original_5127a0_two_owner_order_from_reached(
    sides: tuple[Original5127A0OrderedSide,Original5127A0OrderedSide],
) -> Original5127A0OrderReceipt:
    """Require both EBX=0 then EBX=1 complete, ordered, and source-addressed.

    Source roster entries must use the same canonical original DBRPlayer
    IDs as actual reached per-row records. Original rows, however, expose
    player POINTERS; the independent pointer->native-ID map must be passed
    in another source-qualified layer before this proof is usable.
    To avoid inventing that mapping, enforce rows as native pointer keys
    and distinct side roster sequence as native player IDs. The ordering
    receipt remains a bounded source control-flow validation, NOT a
    completed native player identity or GameState transaction.
    """
    if type(sides) is not tuple or len(sides)!=2:
        raise Original5127A0OrderError("exact two original match-owner passes required")
    counts={"return":0,"row":0,"extra":0,"avail":0}
    for pass_index,side in enumerate(sides):
        if not isinstance(side,Original5127A0OrderedSide) or type(side.pass_index) is not int or side.pass_index!=pass_index:
            raise Original5127A0OrderError("original side owner order must be EBX 0 then 1")
        _uint(side.original_615d10_lookup_pointer,32,"615D10 lookup pointer including NULL")
        if type(side.source_roster_ids) is not tuple or not 0<=len(side.source_roster_ids)<=40:
            raise Original5127A0OrderError("actual original side roster IDs 0..40 required")
        for pid in side.source_roster_ids:
            _uint(pid,16,"roster player ID")
        if len(set(side.source_roster_ids))!=len(side.source_roster_ids):
            raise Original5127A0OrderError("duplicate native source roster ID within same side")
        if type(side.source_rows) is not tuple or len(side.source_rows)>18:
            raise Original5127A0OrderError("original side active rows 0..18 required")
        for i,row in enumerate(side.source_rows):
            if (not isinstance(row,Original5127A0RowCall) or
                row.pass_index!=pass_index or row.row_index!=i or
                row.original_4197c0_world_callback_executed):
                raise Original5127A0OrderError("source side row identity/order or callback-evidence mismatch")
        if type(side.source_steps) is not tuple:
            raise Original5127A0OrderError("actually reached ordered source step tuple required")
        expected=_expected_steps(side)
        if len(side.source_steps)!=len(expected):
            raise Original5127A0OrderError("missing/extra native source callback stage")
        for got,(phase,pid,rowindex,row) in zip(side.source_steps,expected):
            if (not isinstance(got,Original5127A0OrderedStep)
                or got.phase!=phase
                or type(got.original_player_id) is not int
                or got.original_player_id!=pid
                or got.original_row_index!=rowindex
                or got.original_row != row):
                raise Original5127A0OrderError("original source order/owner/player/row mismatch")
            if phase=="avail":
                rcpt=got.original_availability
                if (not isinstance(rcpt,Original419680AvailabilityReceipt)
                    or rcpt.original_419680_native_callback_executed
                    or rcpt.live_game_state_updated
                    or rcpt.original_player_id!=pid
                    or rcpt.original_calendar_lookup_nonnull!=bool(side.original_615d10_lookup_pointer)
                    or got.original_lookup_pointer_used!=side.original_615d10_lookup_pointer):
                    raise Original5127A0OrderError(
                        "source post-row 419680 player/NULL calendar pointer mismatch")
            elif (got.original_availability is not None or
                  got.original_lookup_pointer_used is not None):
                raise Original5127A0OrderError("original non-availability phase cannot borrow 419680 evidence")
            counts[phase]+=1
    return Original5127A0OrderReceipt(
        counts["return"],counts["row"],counts["extra"],counts["avail"],(0,1),
    )
