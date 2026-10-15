"""Bounded source-exact original 418050 eligibility for 409C90 non-2/3 teams.

Authorized original footballmanager.exe: 4,714,541 bytes, SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Independent static x86 source trace: 418050..418125, 41B360, 41B490,
41B4D0, 419350, 4E9BE0. The virtual +30, 4F8E40, 419350,
41B4D0 and other original callbacks are NOT executed by this projector.
For a call requiring externally reached outcomes, insist on EXACT reached
source facts; NEVER synthesize a decision from a reconstructed team.
"""
from dataclasses import dataclass
from struct import unpack_from

class Original418050SourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal418050Eligibility:
    original_player_record_at_418050: bytes
    original_player_record_at_reached_41b490: bytes
    original_player_word_id: int
    original_signed_current_owner_word10: int
    original_source_club_key: int
    original_owner_pointer_at_call: int
    original_initial_bl_nonzero: bool
    original_reached_call_sites: tuple[int,...]
    original_final_41b490_bit11: bool
    original_source_return_al_nonzero: bool
    original_41b4d0_returned_record_pointer_if_reached: int | None
    native_418050_executed: bool = False
    original_dynamic_callbacks_executed: bool = False
    live_player_or_match_world_modified: bool = False

def _u32(v,what):
    if type(v) is not int or not 0 <= v <= 0xffffffff:
        raise Original418050SourceError("actual unsigned native DWORD " + what + " required")
    return v

def _signed32(v):
    return v if v < 0x80000000 else v-0x100000000

def source_original_418050_reached_availability(
    *, original_player_record_at_418050: bytes,
    original_club_key_dword_arg1: int,
    original_dynamic_owner_ptr_arg2: int,
    original_dynamic_owner_record_if_reached: bytes | None = None,
    original_4f8e40_al_if_reached: bool | None = None,
    original_first_419350_signed_dword_if_reached: int | None = None,
    original_second_419350_signed_dword_if_reached: int | None = None,
    original_global_8755e8_mode_if_reached: int | None = None,
    original_global_threshold_8755ec_or_f0_if_reached: int | None = None,
    original_dynamic_owner_vtable30_al_if_reached: bool | None = None,
    original_player_record_at_reached_41b490: bytes,
    original_41b4d0_returned_pointer_if_reached: int | None = None,
    original_41b4d0_returned_record_if_reached: bytes | None = None,
    original_global_9847fc_current_day_if_reached: int | None = None,
) -> SourceOriginal418050Eligibility:
    """Project native 418050 AL without performing its mutable callbacks.

    Initial BL=(BYTE player+14 &7)!=0 OR signed player+10 != full team key.
    When owner pointer exists and player DWORD+174 bit8 SET:
      41B360 true -> owner+34 type1: 4F8E40, first 419350 signed
      DWORD. If <0, skip extra. Otherwise inspect global 8755E8
      case1/2 and optional second 419350>threshold (signed).
      owner+34 !=1: vtable+30 AL true skips; false visits 4F8E40.
    Irrespective of prior route, 41B490 reads player+14 BIT11 on an
    independently reached at-call player record. When it is SET,
    41B4D0 returns a *possibly mutating* record owner; 4E9BE0 tests
    global signed day <= owner+14 signed. On TRUE, return BL;
    otherwise return literal AL1. Without bit11, simply return BL.
    """
    p=original_player_record_at_418050
    later=original_player_record_at_reached_41b490
    if type(p) is not bytes or len(p)<0x178:
        raise Original418050SourceError("original player +174 and +14 bytes mandatory")
    if type(later) is not bytes or len(later)<0x18:
        raise Original418050SourceError("independently reached original player at 41B490 required")
    key=_u32(original_club_key_dword_arg1,"club key")
    owner=_u32(original_dynamic_owner_ptr_arg2,"dynamic owner pointer")
    signed_owner=unpack_from("<h",p,0x10)[0]
    word_id=unpack_from("<H",p,4)[0]
    flags14=unpack_from("<I",p,0x14)[0]
    flags174=unpack_from("<I",p,0x174)[0]
    initial=bool(flags14&7 or (signed_owner&0xffffffff)!=key)
    current=int(initial)
    reached=[]
    numeric=(original_first_419350_signed_dword_if_reached,
             original_second_419350_signed_dword_if_reached,
             original_global_8755e8_mode_if_reached,
             original_global_threshold_8755ec_or_f0_if_reached)
    callbacks=(original_4f8e40_al_if_reached,
               original_dynamic_owner_vtable30_al_if_reached)
    # Native 41807B visits read-only 41B360 whenever owner!=0, EVEN if
    # its player+174 bit8 return is zero and all later owner work is skipped.
    if owner:
        reached.append(0x41B360)
    if owner==0 or not(flags174&0x100):
        if later!=p:
            raise Original418050SourceError(
                "read-only/no owner callback path cannot modify the player before 41B490")
        if (original_dynamic_owner_record_if_reached is not None or
            any(x is not None for x in numeric+callbacks)):
            raise Original418050SourceError("unreached original dynamic owner callback values supplied")
    else:
        # 41B360 was called with +174 bit8 and requires a nonzero owner.
        if (type(original_dynamic_owner_record_if_reached) is not bytes or
                len(original_dynamic_owner_record_if_reached)<0x38):
            raise Original418050SourceError("reached native owner through +34 bytes mandatory")
        type34=unpack_from("<I",original_dynamic_owner_record_if_reached,0x34)[0]
        if type34==1:
            if original_dynamic_owner_vtable30_al_if_reached is not None:
                raise Original418050SourceError("owner +34==1 skips vtable+30")
            if type(original_4f8e40_al_if_reached) is not bool:
                raise Original418050SourceError("reached original 4F8E40 AL mandatory")
            reached.append(0x4F8E40)
            if original_4f8e40_al_if_reached:
                current=1
            first=original_first_419350_signed_dword_if_reached
            if type(first) is not int or not -0x80000000<=first<=0x7fffffff:
                raise Original418050SourceError("first original 419350 signed DWORD mandatory")
            reached.append(0x419350)
            if first<0:
                if any(x is not None for x in numeric[1:]):
                    raise Original418050SourceError("first 419350 negative skips global/second callbacks")
            else:
                mode=original_global_8755e8_mode_if_reached
                if type(mode) is not int or not 0<=mode<=0xffffffff:
                    raise Original418050SourceError("reached global original 8755E8 DWORD required")
                if mode in (1,2):
                    threshold=original_global_threshold_8755ec_or_f0_if_reached
                    second=original_second_419350_signed_dword_if_reached
                    if (type(threshold) is not int or not -0x80000000<=threshold<=0x7fffffff or
                            type(second) is not int or not -0x80000000<=second<=0x7fffffff):
                        raise Original418050SourceError(
                            "reached original threshold and second 419350 signed DWORD required")
                    reached.append(0x419350)
                    if second>threshold:
                        current=1
                elif (original_global_threshold_8755ec_or_f0_if_reached is not None or
                      original_second_419350_signed_dword_if_reached is not None):
                    raise Original418050SourceError("original 8755E8 not 1/2 skips second threshold read")
        else:
            if any(x is not None for x in numeric):
                raise Original418050SourceError("non-type1 owner skips 419350 and global thresholds")
            v=original_dynamic_owner_vtable30_al_if_reached
            if type(v) is not bool:
                raise Original418050SourceError("native dynamic owner vtable+30 AL mandatory")
            reached.append(0x4180E4)
            if v:
                if original_4f8e40_al_if_reached is not None:
                    raise Original418050SourceError("vtable+30 true skips original 4F8E40")
            else:
                if type(original_4f8e40_al_if_reached) is not bool:
                    raise Original418050SourceError("reached native 4F8E40 AL mandatory")
                reached.append(0x4F8E40)
                if original_4f8e40_al_if_reached:
                    current=1

    # Original 41B490 is always invoked at 418102 after every owner branch.
    reached.append(0x41B490)
    bit11=bool(unpack_from("<I",later,0x14)[0]&0x800)
    optional=(original_41b4d0_returned_pointer_if_reached,
              original_41b4d0_returned_record_if_reached,
              original_global_9847fc_current_day_if_reached)
    if bit11:
        ptr=original_41b4d0_returned_pointer_if_reached
        rec=original_41b4d0_returned_record_if_reached
        day=original_global_9847fc_current_day_if_reached
        if (type(ptr) is not int or not 0<ptr<=0xffffffff or
                type(rec) is not bytes or len(rec)<0x18 or
                type(day) is not int or not 0<=day<=0xffffffff):
            raise Original418050SourceError("reached 41B4D0 record pointer and 4E9BE0 day required")
        reached.extend((0x41B4D0,0x4E9BE0))
        if _signed32(day)>unpack_from("<i",rec,0x14)[0]:
            current=1
    else:
        if any(x is not None for x in optional):
            raise Original418050SourceError("unreached 41B4D0/4E9BE0 data supplied")
    return SourceOriginal418050Eligibility(
        p,later,word_id,signed_owner,key,owner,initial,tuple(reached),
        bit11,bool(current),
        original_41b4d0_returned_pointer_if_reached if bit11 else None)
