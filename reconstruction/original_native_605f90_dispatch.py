"""Original source 0x605F70/0x605F90 optional player event pre-dispatch.

Static source: privately retained original footballmanager.exe, 4,714,541
bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
No original binary execution, virtual dispatch, RNG call, message delivery,
heap ownership claim or live GameState mutation. The handler selected below
HAS original further RNG/player/club/queue effects: explicitly outstanding.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into,unpack_from

from original_native_41a5b0_extra_event import Original41A5B0ExtraEventReceipt


class Original605F90SourceError(ValueError):
    pass


# 6060E0 uses initial mutable .data threshold source addresses in this
# exact order, notably skipping 8222F4. Last handler is the fallthrough.
_THRESHOLDS_BY_SUBTYPE = {
    0: (0x8222c0,0x8222c4,0x8222c8,0x8222cc,0x8222d0,
        0x8222d4,0x8222d8,0x8222dc,0x8222e0,0x8222e4,
        0x8222e8,0x8222ec,0x8222f0,0x8222f8),
    1: (0x8222fc,0x822300,0x822304,0x822308,0x82230c,
        0x822310,0x822314,0x822318),
    2: (0x8222fc,0x822300,0x822304,0x822308,0x822310),
}
_HANDLERS_BY_SUBTYPE = {
    0: (0x606300,0x606540,0x606d20,0x607270,0x6074e0,
        0x607cc0,0x6084a0,0x608a00,0x6091e0,0x6098c0,
        0x609b30,0x609da0,0x60a160,0x60a3d0,0x60a630),
    1: (0x606540,0x606d20,0x6074e0,0x607cc0,0x6084a0,
        0x608a00,0x6091e0,0x6098c0,0x609b30),
    2: (0x606540,0x606d20,0x6074e0,0x607cc0,0x608a00,0x6091e0),
}


def _u32(value: int, name: str, allow_zero: bool = False) -> int:
    if type(value) is not int or not 0<=value<=0xffffffff or (value==0 and not allow_zero):
        raise Original605F90SourceError(f"actual source {name} uint32 required")
    return value


@dataclass(frozen=True)
class Original605F90Thresholds:
    """Reached signed int32 mutable globals in NATIVE read/compare order."""
    original_source_addresses: tuple[int,...]
    original_reached_signed_values: tuple[int,...]


@dataclass(frozen=True)
class Original605F90DispatchReceipt:
    original_subtype: int
    original_rng100_result: int
    original_native_threshold_addresses: tuple[int,...]
    original_first_matching_threshold_index: int | None
    original_selected_handler_address: int
    original_rng_draws_consumed_through_selector: int = 1
    original_handler_executed: bool = False
    original_pending_world_event_delivered: bool = False
    live_game_state_mutated: bool = False


def source_original_605f90_select_handler(
    *, original_subtype: int, original_reached_rng100_result: int,
    original_reached_thresholds: Original605F90Thresholds,
) -> Original605F90DispatchReceipt:
    """Source 6060E0/6061F0/606290 first RNG(100), signed >= branch gates.

    Mutable thresholds are NOT necessarily sorted, constant or percentages.
    Native uses the FIRST signed (rng < threshold) condition. A negative
    threshold or threshold >100 must not be silently clamped.
    """
    if type(original_subtype) is not int or original_subtype not in (0,1,2):
        raise Original605F90SourceError("native 605F90 subtype 0,1,2 required")
    if (type(original_reached_rng100_result) is not int or
            not 0<=original_reached_rng100_result<100):
        raise Original605F90SourceError("actual reached 64D540(100) result 0..99 required")
    thresholds=original_reached_thresholds
    if not isinstance(thresholds,Original605F90Thresholds):
        raise Original605F90SourceError("source reached threshold record required")
    expected=_THRESHOLDS_BY_SUBTYPE[original_subtype]
    if (type(thresholds.original_source_addresses) is not tuple or
        type(thresholds.original_reached_signed_values) is not tuple or
        thresholds.original_source_addresses != expected or
        len(thresholds.original_reached_signed_values) != len(expected)):
        raise Original605F90SourceError("exact native mutable threshold address coverage required")
    selected=None
    for i,value in enumerate(thresholds.original_reached_signed_values):
        if type(value) is not int or not -0x80000000<=value<=0x7fffffff:
            raise Original605F90SourceError("native signed32 mutable threshold values required")
        if selected is None and original_reached_rng100_result < value:
            selected=i
    handler=_HANDLERS_BY_SUBTYPE[original_subtype][
        len(expected) if selected is None else selected
    ]
    return Original605F90DispatchReceipt(
        original_subtype,original_reached_rng100_result,expected,
        selected,handler,
    )


@dataclass(frozen=True)
class Original605F90ReachedCall:
    """A positive original 41A5B0 source event reaches 605F90 only after malloc.

    The first and second native resolver virtual calls must return native
    DBRPlayer snapshots; they are separately reached and may not be
    substituted with each other.
    """
    original_caller: Original41A5B0ExtraEventReceipt
    original_allocated_descriptor_pointer: int
    original_descriptor_after_605f70: bytes
    original_player_after_41a5b0_pointer_store: bytes
    original_first_resolved_native_player: bytes
    original_second_resolved_native_player: bytes
    original_rng100_result: int
    original_mutable_thresholds: Original605F90Thresholds


@dataclass(frozen=True)
class Original605F90PreDispatchReceipt:
    original_player_id: int
    original_subtype: int
    original_descriptor_pointer: int
    original_descriptor_at_subhandler_entry: bytes
    original_handler_choice: Original605F90DispatchReceipt
    original_first_getter_returned_id: int
    original_second_getter_returned_id: int
    original_native_handler_executed: bool = False
    original_allocated_descriptor_freed: bool = False
    original_player24c_lifecycle_complete: bool = False
    original_event_delivery_verified: bool = False
    live_game_state_updated: bool = False


def source_original_605f90_predispatch_from_reached(
    reached: Original605F90ReachedCall,
) -> Original605F90PreDispatchReceipt:
    """Model 41A5B0 allocation -> 605F70 -> 605F90 up to RNG handler call.

    Original 605F70 sets DWORD+0=-1, BYTE+4=3, BYTE+5=4; bytes+6..+11
    are not initialized in this constructor. The original caller writes
    descriptor pointer into DBRPlayer+24C, then 605F90 sets BYTE+4
    subtype and DWORD+8 to the independently resolved player+4 ID.
    If allocator returned zero, the native caller would still attempt to
    dereference it: fail closed rather than invent allocation success.
    """
    if not isinstance(reached,Original605F90ReachedCall):
        raise Original605F90SourceError("actual 605F90 reached call required")
    caller=reached.original_caller
    if (not isinstance(caller,Original41A5B0ExtraEventReceipt) or
        caller.original_native_callback_executed or caller.live_game_state_updated or
        not caller.original_would_allocate_605f70_and_store_player24c or
        caller.source_branch_complete_without_world_effects or
        caller.original_605f90_subtype_if_allocated not in (0,1)):
        raise Original605F90SourceError("source-positive original 41A5B0 descriptor call required")
    address=_u32(reached.original_allocated_descriptor_pointer,"allocated 12-byte descriptor")
    descriptor=reached.original_descriptor_after_605f70
    if (type(descriptor) is not bytes or len(descriptor)!=12 or
        unpack_from("<I",descriptor,0)[0]!=0xffffffff or
        descriptor[4]!=3 or descriptor[5]!=4):
        raise Original605F90SourceError("original 605F70 descriptor constructor fields invalid")
    p=reached.original_player_after_41a5b0_pointer_store
    prior=caller.original_player_after_row_at_call
    if (type(p) is not bytes or len(p)<0x250 or type(prior) is not bytes or
        len(prior)!=len(p) or
        p[:0x24c]!=prior[:0x24c] or p[0x250:]!=prior[0x250:] or
        unpack_from("<I",p,0x24c)[0]!=address):
        raise Original605F90SourceError("original player+24C allocation/store state differs from reached row")
    wanted=caller.original_player_id
    got=[]
    for i,raw in enumerate((
        reached.original_first_resolved_native_player,
        reached.original_second_resolved_native_player,
    )):
        if type(raw) is not bytes or len(raw)<6:
            raise Original605F90SourceError(f"native player getter {i+1} source +4 bytes required")
        pid=unpack_from("<H",raw,4)[0]
        if pid != wanted:
            raise Original605F90SourceError("native first/second getter player ID mismatch")
        got.append(pid)
    subtype=caller.original_605f90_subtype_if_allocated
    dispatch=source_original_605f90_select_handler(
        original_subtype=subtype,
        original_reached_rng100_result=reached.original_rng100_result,
        original_reached_thresholds=reached.original_mutable_thresholds,
    )
    next_bytes=bytearray(descriptor)
    next_bytes[4]=subtype
    pack_into("<I",next_bytes,8,got[1])
    return Original605F90PreDispatchReceipt(
        wanted,subtype,address,bytes(next_bytes),dispatch,got[0],got[1],
    )



@dataclass(frozen=True)
class Original606540Reached:
    """Reached 606540 common subtype handler from a qualified 605F90 plan."""
    original_predispatch: Original605F90PreDispatchReceipt
    original_first_rng_result: int
    original_822320_first_threshold: int
    original_822324_second_threshold: int | None = None
    original_822328_third_threshold: int | None = None
    original_second_rng4_result: int | None = None
    original_82232c_short_base: int | None = None
    original_822330_medium_base: int | None = None
    original_822334_long_base: int | None = None


@dataclass(frozen=True)
class Original606540PreHumanReceipt:
    original_player_id: int
    original_subtype: int
    original_source_descriptor_before_417340: bytes
    original_first_rng_bound: int
    original_first_rng_result: int
    original_second_rng4_reached: bool
    original_schedule_base_from_mutable_source: int
    original_schedule_delta_from_rng: int
    original_handler_417340_callback_outstanding: bool = True
    original_60aa20_descriptor_schedule_callback_outstanding: bool = True
    original_event_pending_or_delivered: bool = False
    live_game_state_updated: bool = False


def _signed32(value: int | None, name: str) -> int:
    if type(value) is not int or not -0x80000000<=value<=0x7fffffff:
        raise Original605F90SourceError(f"actual original {name} signed32 required")
    return value


def source_original_606540_pre_human_from_reached(
    reached: Original606540Reached,
) -> Original606540PreHumanReceipt:
    """Source 606540..60661D until native owner 417340 (unexecuted).

    Original subtype2 first draws 64D540(75); subtype0/1 draw
    64D540(100). Native 822320 early branch sets descriptor+5 to 0
    with static/source duration global+82232C. Other branches need
    optional 64D540(4) with +3 or +11, descriptor+5=1/2/3.
    The function THEN conditionally allocates native manager notifications
    and calls 60AA20. This is only a bounded pre-human source projection.
    """
    if not isinstance(reached,Original606540Reached):
        raise Original605F90SourceError("qualified original 606540 reached source required")
    prev=reached.original_predispatch
    if (not isinstance(prev,Original605F90PreDispatchReceipt) or
            prev.original_handler_choice.original_selected_handler_address!=0x606540 or
            prev.original_native_handler_executed or
            prev.live_game_state_updated):
        raise Original605F90SourceError("original 605F90 must choose 606540 first")
    subtype=prev.original_subtype
    if (type(subtype) is not int or subtype not in (0,1,2) or
        prev.original_handler_choice.original_subtype!=subtype or
        prev.original_descriptor_at_subhandler_entry[4]!=subtype):
        raise Original605F90SourceError("native 606540 subtype/descriptor choice mismatch")
    bound=75 if subtype==2 else 100
    r=reached.original_first_rng_result
    if type(r) is not int or not 0<=r<bound:
        raise Original605F90SourceError("reached 606540 first RNG(75/100) result required")
    t0=_signed32(reached.original_822320_first_threshold,"822320 first threshold")
    desc=bytearray(prev.original_descriptor_at_subhandler_entry)
    if type(desc) is not bytearray or len(desc)!=12:
        raise Original605F90SourceError("native 606540 actual descriptor required")
    if r<t0:
        if any(v is not None for v in (
            reached.original_822324_second_threshold,
            reached.original_822328_third_threshold,
            reached.original_second_rng4_result,
            reached.original_822330_medium_base,
            reached.original_822334_long_base)):
            raise Original605F90SourceError("606540 early branch skips second thresholds and RNG")
        base=_signed32(reached.original_82232c_short_base,"82232C short base")
        desc[5]=0
        delta=1
        second=False
    else:
        if reached.original_82232c_short_base is not None:
            raise Original605F90SourceError("606540 nonshort branch skips 82232C base")
        t1=_signed32(reached.original_822324_second_threshold,"822324 second threshold")
        final_long=r>=t1 and subtype!=2
        if final_long:
            t2=_signed32(reached.original_822328_third_threshold,"822328 third threshold")
            if r<t2:
                desc[5]=2
            else:
                desc[5]=3
            base=_signed32(reached.original_822334_long_base,"822334 long base")
            if reached.original_822330_medium_base is not None:
                raise Original605F90SourceError("606540 long path skips medium base")
            offset=11
        else:
            if reached.original_822328_third_threshold is not None or reached.original_822334_long_base is not None:
                raise Original605F90SourceError("606540 medium path skips third threshold/long base")
            desc[5]=1
            base=_signed32(reached.original_822330_medium_base,"822330 medium base")
            offset=3
        subdraw=reached.original_second_rng4_result
        if type(subdraw) is not int or not 0<=subdraw<4:
            raise Original605F90SourceError("native second 606540 RNG(4) result required")
        delta=subdraw+offset
        second=True
    return Original606540PreHumanReceipt(
        original_player_id=prev.original_player_id,
        original_subtype=subtype,
        original_source_descriptor_before_417340=bytes(desc),
        original_first_rng_bound=bound,
        original_first_rng_result=r,
        original_second_rng4_reached=second,
        original_schedule_base_from_mutable_source=base,
        original_schedule_delta_from_rng=delta,
    )
