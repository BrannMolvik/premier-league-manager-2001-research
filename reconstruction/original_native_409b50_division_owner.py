"""Original 403E10→409500→409B50+1D8 source-only player-world wrapper.

Canonical private original footballmanager.exe (4,714,541 bytes,
SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3),
static x86 only; never launched or committed. Original 403E10 can
MUTATE native team+0x40 sentinel when the global 875628 indexed owner
DWORD+0x24 is FFFFFFFF. Original 409500 is dynamic and may mutate
world. The wrapper requires its reached exact EAX and independently
reached post-409C90 team snapshot; no callback executed or GameState
written. Do NOT treat team+1D8 as match score.
"""
from dataclasses import dataclass
from struct import unpack_from, pack_into


class Original409B50SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal403E10CompetitionOwner:
    original_native_team_pointer: int
    original_team_record_before: bytes
    original_reached_875628_base: int|None
    original_reached_indexed_875628_record_if_needed: bytes|None
    original_source_team_after_optional_plus40_write: bytes
    original_return_eax_nonzero: bool
    native_403e10_executed: bool = False
    live_world_mutated: bool = False


def source_original_403e10_competition_owner_gate(
    *, original_native_team_pointer: int,
    original_native_team_record_before_403e10: bytes,
    original_global_875628_base_if_index_reached: int|None = None,
    original_global_875628_indexed_record_if_reached: bytes|None = None,
) -> SourceOriginal403E10CompetitionOwner:
    """At 403E10: team+40 DWORD==FFFFFFFF skips global lookup, returns0.
    Else original 875628 + team+40 *64 record DWORD+24 == FFFFFFFF
    sets team+40 to FFFFFFFF and returns0. Otherwise returns AL1.
    This is an immutable original byte-level projection, not native mutation.
    """
    ptr=original_native_team_pointer
    t=original_native_team_record_before_403e10
    if type(ptr) is not int or not 0<ptr<=0xffffffff:
        raise Original409B50SourceError("actual native source team object pointer required")
    if type(t) is not bytes or len(t)<0x1e0:
        raise Original409B50SourceError("actual source native team fields +40 and +1D8 required")
    idx=unpack_from("<I",t,0x40)[0]
    base=original_global_875628_base_if_index_reached
    rec=original_global_875628_indexed_record_if_reached
    out=bytearray(t)
    if idx==0xffffffff:
        if base is not None or rec is not None:
            raise Original409B50SourceError("team+40 sentinel skips original 875628 lookup")
        active=False
    else:
        if (type(base) is not int or not 0<base<=0xffffffff or
                base +idx*0x40 >0xffffffff or
                type(rec) is not bytes or len(rec)<0x28):
            raise Original409B50SourceError(
                "original reached 875628+clubindex*64 +24 owner DWORD required")
        if unpack_from("<I",rec,0x24)[0]==0xffffffff:
            pack_into("<I",out,0x40,0xffffffff)
            active=False
        else:
            active=True
    return SourceOriginal403E10CompetitionOwner(
        ptr,t,base,rec,bytes(out),active)


@dataclass(frozen=True)
class SourceOriginal409B50After409C90:
    original_403e10_owner_gate: SourceOriginal403E10CompetitionOwner
    original_409500_reached_return_eax_if_gate_nonzero: int|None
    original_global_875628_record_if_409500_result0_to3: bytes|None
    original_409b50_selected_edi_dword_for_409c90: int
    original_409b50_source_indexed_byte_offset_if_reached: int|None
    original_native_team_at_post_409c90_before_store: bytes
    original_native_team_after_409bd0_literal_store: bytes
    original_409b50_409c90_called_unconditionally: bool
    native_409500_executed: bool = False
    native_409c90_executed: bool = False
    native_409bd0_executed: bool = False
    original_live_game_state_mutated: bool = False


def source_original_409b50_select_edi_and_write_team_plus1d8(
    *, original_403e10_owner_gate: SourceOriginal403E10CompetitionOwner,
    original_reached_409500_return_eax_if_403e10_true: int|None,
    original_reached_875628_indexed_record_at_409b72_if_valid_mode: bytes|None,
    original_native_team_record_post_409c90_pre_409bd0: bytes,
) -> SourceOriginal409B50After409C90:
    """Exact original 409B50 AL gate, 409500 4-way EAX dispatch,
    global 875628 indexed 0x40-stride BYTE offsets +20/+22/+20/+21,
    unconditional 409C90 call, then original +1D8 EDI store.

    Note: the original 409B50 THISCALL passes EDI and +1DC plus
    other caller stack inputs into 409C90. The actual callback can
    mutate original player, status and team fields; caller supplies
    real *post*-409C90 team bytes, not its entry snapshot.
    """
    c=original_403e10_owner_gate
    if type(c) is not SourceOriginal403E10CompetitionOwner:
        raise Original409B50SourceError("actual native source 403E10 receipt required")
    mode=original_reached_409500_return_eax_if_403e10_true
    rec=original_reached_875628_indexed_record_at_409b72_if_valid_mode
    post=original_native_team_record_post_409c90_pre_409bd0
    if type(post) is not bytes or len(post)<0x1e0:
        raise Original409B50SourceError(
            "independent actual post-409C90 native team through +1D8 is required")
    edi=0
    offset=None
    if not c.original_return_eax_nonzero:
        if mode is not None or rec is not None:
            raise Original409B50SourceError("403E10 false skips native 409500 and 875628 BYTE")
    else:
        if type(mode) is not int or not 0<=mode<=0xffffffff:
            raise Original409B50SourceError(
                "reached native 409500 EAX DWORD mandatory after true 403E10")
        if mode<=3:
            offsets=(0x20,0x22,0x20,0x21)
            offset=offsets[mode]
            if type(rec) is not bytes or len(rec)<0x40:
                raise Original409B50SourceError(
                    "actual original 875628 source 64-byte record mandatory")
            # The global+clubindex record is the same native indexed
            # owner that 403E10 visited, unless original 409500 has
            # mutated the shared 875628 table. Explicit post-callback
            # bytes, not a pre-call cached record, are authoritative.
            edi=rec[offset]
        elif rec is not None:
            raise Original409B50SourceError("409500 EAX>3 unsigned skips global source BYTE")
    out=bytearray(post)
    pack_into("<I",out,0x1d8,edi)
    return SourceOriginal409B50After409C90(
        c,mode,rec,edi,offset,post,bytes(out),True)
