"""Bounded static original 407770(arg0 or arg1) eligibility source.

Only the *reached* native call branch is projected. Inputs for 4EA300,
403640, 407EC0/407220 and 406BE0 are ORIGINAL independent callback
outputs; no portable team or reconstructed lineup is allowed to invent them.
Original executable SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This module does not execute native callbacks, diagnostics, team writes,
GameState, PResults, match calculation or SaveLoad.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original407770SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal407770PlayerDayResult:
    original_roster_player_word_id: int
    original_reached_4ea300_signed_eax: int


@dataclass(frozen=True)
class SourceOriginal407770Eligibility:
    original_arg_nonzero: bool
    original_roster_count_signed: int
    original_return_eax_nonzero: bool
    reached_4ea300_player_ids: tuple[int, ...]
    native_407770_executed: bool = False
    native_subcallbacks_executed: bool = False
    complete_original_roster_world_proven: bool = False
    live_game_state_modified: bool = False


def _signed32(x: object, field: str) -> int:
    if type(x) is not int or not -0x80000000 <= x <= 0x7fffffff:
        raise Original407770SourceError(f"actual signed DWORD {field} required")
    return x


def source_original_407770_reached_roster_gate(
    *,
    original_team_record: bytes,
    original_407770_argument: int,
    original_current_day_874b64_if_arg0: int | None = None,
    original_reached_4ea300_player_results_if_arg0:
        tuple[SourceOriginal407770PlayerDayResult, ...] | None = None,
    original_reached_403640_al_if_arg1: bool | None = None,
    original_team_name_first_byte_if_reached: int | None = None,
    original_reached_407220_edi_if_arg1: int | None = None,
    original_reached_406be0_eax_if_arg1: int | None = None,
) -> SourceOriginal407770Eligibility:
    """Projection of original 40777B..40789C, NOT a runtime roster validation.

    Native signed roster count at team+294 must be >=11. Below that
    original performs 407060/407940/66876F diagnostic callbacks and
    unconditionally returns zero, regardless of argument.

    With arg0 (zero), each 16-bit roster ID at team+244 in order is
    resolved through 875640 lookup and checked by actual 4EA300(0).
    It returns zero on first signed EAX >= original global day 874B64
    or EAX <=0; otherwise after all count entries it returns one.

    With arg1 (nonzero), 403640 AL or actual team+8 leading '!' forces
    EDI=11. Otherwise 407EC0 and 407220(4) produce the native EDI.
    Original 406BE0(1,0) then returns EAX. Only EDI==11 AND EAX==1
    returns nonzero. No callback result may be inferred from a modern XI.
    """
    if type(original_team_record) is not bytes or len(original_team_record)<0x298:
        raise Original407770SourceError("actual original team record through +294 required")
    if type(original_407770_argument) is not int or original_407770_argument not in (0,1):
        raise Original407770SourceError("source-specific 407770 argument 0 or 1 required")
    count=unpack_from('<i',original_team_record,0x294)[0]
    arg1=original_407770_argument==1
    all_arg0=(original_current_day_874b64_if_arg0,
              original_reached_4ea300_player_results_if_arg0)
    all_arg1=(original_reached_403640_al_if_arg1,
              original_team_name_first_byte_if_reached,
              original_reached_407220_edi_if_arg1,
              original_reached_406be0_eax_if_arg1)
    if count<11:
        if any(v is not None for v in all_arg0+all_arg1):
            raise Original407770SourceError("roster<11 short-circuits before other supplied predicates")
        return SourceOriginal407770Eligibility(arg1,count,False,())
    if len(original_team_record)<0x244+2*count:
        raise Original407770SourceError("source original ordered roster WORDs missing")
    if arg1:
        if any(v is not None for v in all_arg0):
            raise Original407770SourceError("arg1 never calls roster-day 4EA300 gate")
        if type(original_reached_403640_al_if_arg1) is not bool:
            raise Original407770SourceError("reached original 403640 AL required")
        if type(original_reached_406be0_eax_if_arg1) is not int:
            raise Original407770SourceError("actual reached original 406BE0 EAX required")
        eax=_signed32(original_reached_406be0_eax_if_arg1,"406BE0")
        if original_reached_403640_al_if_arg1:
            if (original_team_name_first_byte_if_reached is not None or
                    original_reached_407220_edi_if_arg1 is not None):
                raise Original407770SourceError("unreached team name and 407220 supplied")
            edi=11
        else:
            first=original_team_name_first_byte_if_reached
            if type(first) is not int or not 0<=first<=255:
                raise Original407770SourceError("actual team+8 name first byte required")
            if first==0x21:
                if original_reached_407220_edi_if_arg1 is not None:
                    raise Original407770SourceError("team name '!' skips 407220")
                edi=11
            else:
                edi=_signed32(original_reached_407220_edi_if_arg1,"407220")
        return SourceOriginal407770Eligibility(True,count,edi==11 and eax==1,())
    if any(v is not None for v in all_arg1):
        raise Original407770SourceError("arg0 does not call 403640/407220/406BE0")
    day=_signed32(original_current_day_874b64_if_arg0,"874B64")
    replies=original_reached_4ea300_player_results_if_arg0
    if type(replies) is not tuple:
        raise Original407770SourceError("actual ordered reached 4EA300 callbacks tuple required")
    visited=[]
    for index, receipt in enumerate(replies):
        if index>=count or type(receipt) is not SourceOriginal407770PlayerDayResult:
            raise Original407770SourceError("extra/non-native original 4EA300 result")
        pid=unpack_from('<H',original_team_record,0x244+2*index)[0]
        if type(receipt.original_roster_player_word_id) is not int or receipt.original_roster_player_word_id!=pid:
            raise Original407770SourceError("wrong original roster WORD order")
        value=_signed32(receipt.original_reached_4ea300_signed_eax,"4EA300")
        visited.append(pid)
        if value<=0 or value>=day:
            if index+1!=len(replies):
                raise Original407770SourceError("unreached 4EA300 callbacks after first invalid value")
            return SourceOriginal407770Eligibility(False,count,False,tuple(visited))
    if len(visited)!=count:
        raise Original407770SourceError("source 4EA300 results incomplete before success")
    return SourceOriginal407770Eligibility(False,count,True,tuple(visited))
