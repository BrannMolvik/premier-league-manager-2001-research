"""Strict value projection of the original FastView 0x533370 roster stage.

Original owner-approved footballmanager.exe (4,714,541 B; SHA-256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3).
This models only the 0x533A00 native 72-byte per-player value write and
0x533370 8-byte roster status transform. Actual original pointers, the
0x533480 side-header constructor, 0x533AB0 dynamic source flag result,
match simulation, post-modal world writes and UI must be supplied/proved
separately. Original binary is NOT bundled with this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

SOURCE_FASTVIEW_ROSTER_STAGE_VA = 0x533370
SOURCE_FASTVIEW_ROSTER_ROW_VA = 0x533A00
SOURCE_FASTVIEW_ROSTER_PLAYER_FLAG_GETTER_VA = 0x41B490
SOURCE_FASTVIEW_ROSTER_PLAYER_ROLE_GETTER_VA = 0x4EA300
SOURCE_FASTVIEW_ROSTER_PLAYER_STATUS_GETTER_VA = 0x41E3D0
SOURCE_FASTVIEW_ROSTER_EXTERNAL_FLAG_VA = 0x533AB0
SOURCE_FASTVIEW_ROSTER_SIDE_BYTES = 1556
SOURCE_FASTVIEW_ROSTER_ROW_START = 0x104
SOURCE_FASTVIEW_ROSTER_ROW_STRIDE = 0x48
SOURCE_FASTVIEW_ROSTER_COUNT_OFFSET = 0xFC
SOURCE_FASTVIEW_ROSTER_OPTION_OFFSET = 0x100
SOURCE_FASTVIEW_ROSTER_SOURCE_COUNT_OFFSETS = (0x5A4, 0xB54)
SOURCE_FASTVIEW_ROSTER_SOURCE_STATUS_OFFSETS = (0x7C, 0x62C)
SOURCE_FASTVIEW_ROSTER_SOURCE_STRIDE = 0x4C


class SourceFastViewNativePlayerRosterError(ValueError):
    """Unqualified original pointer/value/input cannot enter a stage."""


@dataclass(frozen=True)
class SourceFastViewNativePlayerRowInput:
    """Already-resolved original pointers, in the actual source roster order.

    player_record must contain native +0x248 subobject pointer, though this
    projection NEVER dereferences that pointer; the caller separately resolves
    its original bytes. 'display_name_nul' is the original indirect
    [player+0x0C]->[0] NUL-terminated byte string, not a normalized name.
    'byte8_source' is the original [player+0x08]->[0] byte source.
    """

    player_record: bytes
    player_subobject: bytes
    display_name_nul: bytes
    byte8_source: bytes


def source_fastview_native_side_roster_stage_533370(
    *, original_side_after_533480_header: bytes,
    original_match_object: bytes,
    original_side_index: int,
    original_ordered_player_rows: tuple[SourceFastViewNativePlayerRowInput, ...],
    original_533ab0_result: int,
) -> bytes:
    """Source byte-writes to one 1556-byte side after a proven native header.

    Original native 0x533370 stores side match count +0xFC, builds each
    player via 0x533A00, stores source 0x41E3D0 at row+0x47,
    derives eight clipped status bytes at row+0x39..+0x40, invokes
    0x533480 for the header, then stores 0x533AB0 DWORD at +0x100.
    Caller supplies already-proven 533480 header bytes and the real
    533AB0 return. This is deliberately NOT a complete original match
    owner/side pointer resolver or live-game integration.
    """
    if type(original_side_after_533480_header) is not bytes or len(original_side_after_533480_header) != SOURCE_FASTVIEW_ROSTER_SIDE_BYTES:
        raise SourceFastViewNativePlayerRosterError("original 1556-byte native side/header required")
    if type(original_side_index) is not int or original_side_index not in (0, 1):
        raise SourceFastViewNativePlayerRosterError("native side must be zero or one")
    if type(original_match_object) is not bytes or len(original_match_object) < 0xB58:
        raise SourceFastViewNativePlayerRosterError("native source match must include both side counts and status fields")
    if type(original_ordered_player_rows) is not tuple:
        raise SourceFastViewNativePlayerRosterError("authentic ordered original player tuple required")
    if type(original_533ab0_result) is not int or not 0 <= original_533ab0_result <= 0xFF:
        raise SourceFastViewNativePlayerRosterError("qualified native 0x533AB0 return byte required")

    count = unpack_from("<I", original_match_object,
                        SOURCE_FASTVIEW_ROSTER_SOURCE_COUNT_OFFSETS[original_side_index])[0]
    # Already verified as native side max within its original 1556B storage.
    if count not in range(11, 19) or len(original_ordered_player_rows) != count:
        raise SourceFastViewNativePlayerRosterError("native original 11..18 player count/order required")
    side = bytearray(original_side_after_533480_header)
    pack_into("<I", side, SOURCE_FASTVIEW_ROSTER_COUNT_OFFSET, count)
    for ordinal, row in enumerate(original_ordered_player_rows):
        if type(row) is not SourceFastViewNativePlayerRowInput:
            raise SourceFastViewNativePlayerRosterError("original player row identity required")
        rec, sub, name, byte8 = (row.player_record, row.player_subobject,
                                 row.display_name_nul, row.byte8_source)
        if (type(rec) is not bytes or len(rec) < 0x24C
                or type(sub) is not bytes or len(sub) < 3
                or type(name) is not bytes or not name
                or type(byte8) is not bytes or not byte8):
            raise SourceFastViewNativePlayerRosterError("missing original player pointer targets/record")
        first_nul = name.find(b"\x00")
        if first_nul < 0:
            raise SourceFastViewNativePlayerRosterError("original player name must be NUL-terminated")
        target = SOURCE_FASTVIEW_ROSTER_ROW_START + ordinal * SOURCE_FASTVIEW_ROSTER_ROW_STRIDE
        if target + first_nul + 1 > len(side):
            raise SourceFastViewNativePlayerRosterError("original strcpy would exceed source stage")
        side[target:target + first_nul + 1] = name[:first_nul + 1]
        side[target + 0x20] = byte8[0]
        pack_into("<I", side, target + 0x24, unpack_from("<H", rec, 4)[0])
        pack_into("<I", side, target + 0x28, unpack_from("<H", rec, 0x6E)[0])
        for i in range(3):
            # 0x4EA300 reads BYTE [subobject+index] and zero-extends to DWORD.
            pack_into("<I", side, target + 0x2C + 4*i, sub[i])
        # 0x41B490 returns original player DWORD+0x14 bit11.
        side[target + 0x38] = (unpack_from("<I", rec, 0x14)[0] >> 11) & 1
        # 0x41E3D0 compares signed player+0x10 against exactly the value
        # passed by this caller, so its original reached branch is +0x70.
        side[target + 0x47] = rec[0x70]
        side[target + 0x41:target + 0x45] = rec[0x41:0x45]
        side[target + 0x45:target + 0x47] = rec[0x40:0x41] * 2

        source = (SOURCE_FASTVIEW_ROSTER_SOURCE_STATUS_OFFSETS[original_side_index]
                  + SOURCE_FASTVIEW_ROSTER_SOURCE_STRIDE * ordinal)
        position = original_match_object[source]
        for i in range(8):
            flag = original_match_object[source + 5 + i]
            original_score = position - 5 + (12 if flag else 8)
            side[target + 0x39 + i] = max(0, min(15, original_score))
    pack_into("<I", side, SOURCE_FASTVIEW_ROSTER_OPTION_OFFSET, original_533ab0_result)
    return bytes(side)


SOURCE_FASTVIEW_ROSTER_CLUB_HEADER_VA = 0x533480
SOURCE_FASTVIEW_ROSTER_CLUB_HEADER_ELIGIBILITY_VA = 0x5337C0


def source_fastview_native_side_header_direct_fields_533480(
    *, original_staged_side_1556: bytes,
    original_club_record: bytes,
    original_5337c0_result: bool,
) -> bytes:
    """Only source-direct 0x533480 +0xD4..+0xFA header field writes.

    Native 0x5337C0 conditionally exposes club WORDs +0x84..+0x8A;
    it also consults original external objects/country-mode and is not
    reducible to a standalone boolean from club bytes alone. The caller
    MUST qualify that predicate from original source/runtime. Native
    text, owner pointers, grouped formation, and other +0..+0xD3
    writes are NOT modeled by this helper.
    """
    if type(original_staged_side_1556) is not bytes or len(original_staged_side_1556) != SOURCE_FASTVIEW_ROSTER_SIDE_BYTES:
        raise SourceFastViewNativePlayerRosterError("full native side memory required")
    if type(original_club_record) is not bytes or len(original_club_record) < 0x8C:
        raise SourceFastViewNativePlayerRosterError("source original club record +0x8A required")
    if type(original_5337c0_result) is not bool:
        raise SourceFastViewNativePlayerRosterError("qualified original 0x5337C0 result required")
    if original_5337c0_result and unpack_from('<H', original_club_record, 0x84)[0] == 0:
        raise SourceFastViewNativePlayerRosterError("native 0x5337C0 cannot pass with empty club +0x84")
    side=bytearray(original_staged_side_1556)
    side[0xD4:0xDC]=(original_club_record[0x84:0x8C] if original_5337c0_result
                     else b'\x00'*8)
    first=bytes(((original_club_record[0x44]+1)&0xFF,
                 original_club_record[0x4A],original_club_record[0x4B],original_club_record[0x4C]))
    second=bytes(((original_club_record[0x47]+1)&0xFF,
                  original_club_record[0x56],original_club_record[0x57],original_club_record[0x58]))
    for target,values in ((0xDC,first),(0xE0,second),(0xE4,first),(0xE8,second)):
        side[target:target+4]=values
    # The original deliberately does NOT write +0xEF/+0xF3/+0xF7/+0xFB.
    for target,source in ((0xEC,0x45),(0xED,0x50),(0xEE,0x51),
                          (0xF0,0x48),(0xF1,0x5C),(0xF2,0x5D),
                          (0xF4,0x46),(0xF5,0x53),(0xF6,0x54),
                          (0xF8,0x49),(0xF9,0x5F),(0xFA,0x60)):
        side[target]=original_club_record[source]
    return bytes(side)


SOURCE_FASTVIEW_ROSTER_GROUP_MATCH_VA = 0x5339C0
SOURCE_FASTVIEW_ROSTER_GROUP_TARGET_OFFSETS = (0x90, 0xA8, 0xC0)
SOURCE_FASTVIEW_ROSTER_GROUP_COUNT_OFFSETS = (0x8C, 0xA4, 0xBC)
SOURCE_FASTVIEW_ROSTER_GROUP_MAX = 5


def source_fastview_native_formation_groups_533480(
    *, original_staged_side_1556: bytes,
    original_4037b0_has_formation: bool,
    source_formation_player_id_groups: tuple[tuple[int, ...], ...] | None,
) -> bytes:
    """Exact direct 0x533480/0x5339C0 first-match ordinal index side effects.

    The native code uses a 0x48-byte row stride and reads player DWORD ID
    at staged side+0x128, comparing it to formation WORD IDs. Three group
    input orders use original 0x403850 offsets +0x664/+0x66C/+0x668.
    For each matching ID, the first staged ordinal goes into the group's
    next DWORD slot; missing members do not consume a slot. Each of the
    three output arrays has room for FIVE DWORDs before the next owner
    region; refuse unqualified larger groups rather than corrupting.
    When 0x4037B0 returns zero, original skips the groups and zeroes only
    three count DWORDs; original formation group pointers are not read.
    """
    if type(original_staged_side_1556) is not bytes or len(original_staged_side_1556) != SOURCE_FASTVIEW_ROSTER_SIDE_BYTES:
        raise SourceFastViewNativePlayerRosterError("exact original 1556-byte roster stage required")
    if type(original_4037b0_has_formation) is not bool:
        raise SourceFastViewNativePlayerRosterError("original 0x4037B0 predicate required")
    if not original_4037b0_has_formation:
        if source_formation_player_id_groups is not None:
            raise SourceFastViewNativePlayerRosterError("original unvisited formation cannot be supplied")
        result=bytearray(original_staged_side_1556)
        for offset in SOURCE_FASTVIEW_ROSTER_GROUP_COUNT_OFFSETS:
            pack_into('<I',result,offset,0)
        return bytes(result)
    if (type(source_formation_player_id_groups) is not tuple
        or len(source_formation_player_id_groups) != 3):
        raise SourceFastViewNativePlayerRosterError("three original formation role groups required")
    for group in source_formation_player_id_groups:
        if (type(group) is not tuple or len(group)>SOURCE_FASTVIEW_ROSTER_GROUP_MAX
            or any(type(player_id) is not int or not 0<=player_id<=0xFFFF for player_id in group)):
            raise SourceFastViewNativePlayerRosterError("original formation group must contain 0..5 WORD IDs")
    count=unpack_from('<I',original_staged_side_1556,0xFC)[0]
    if not 11<=count<=18:
        raise SourceFastViewNativePlayerRosterError("authenticated 11..18 original staged player count required")
    source_player_ids=tuple(unpack_from('<I',original_staged_side_1556,0x128+i*0x48)[0]
                            for i in range(count))
    result=bytearray(original_staged_side_1556)
    for group,offset,count_offset in zip(source_formation_player_id_groups,
                                          SOURCE_FASTVIEW_ROSTER_GROUP_TARGET_OFFSETS,
                                          SOURCE_FASTVIEW_ROSTER_GROUP_COUNT_OFFSETS):
        found=[]
        for original_formation_player_id in group:
            try:
                ordinal=source_player_ids.index(original_formation_player_id)
            except ValueError:
                continue
            found.append(ordinal)
        for i,ordinal in enumerate(found):
            pack_into('<I',result,offset+4*i,ordinal)
        pack_into('<I',result,count_offset,len(found))
    return bytes(result)


SOURCE_FASTVIEW_ROSTER_EXTERNAL_OPTIONS_VA = 0x533AB0
SOURCE_FASTVIEW_ROSTER_DEFAULT_OPTION = 11
SOURCE_FASTVIEW_ROSTER_OPTION_REGISTRY_GLOBAL_VA = 0x876C50
SOURCE_FASTVIEW_ROSTER_OPTION_REGISTRY_STRIDE = 0x40
SOURCE_FASTVIEW_ROSTER_OPTION_RECORD_BYTE_OFFSET = 0x2B


def source_fastview_original_side_option_533ab0(
    *, original_club_word18: int,
    original_62ac80_virtual30_result: int | None,
    original_62ac80_signed_word20: int | None,
    original_computed_registry_pointer_nonzero: bool | None,
    original_registry_slot_bytes: bytes | None,
) -> int:
    """0x533AB0's conditional default11 vs original mode/registry BYTE+0x2B.

    The original club pointer is from 0x405890(match side club). When its
    WORD+0x18 is zero, return 11 without reading any other source. Else
    0x62AC80(match)->+0x4C selects a separate owner; its virtual+0x30
    returns AL. Nonzero returns 11. Zero allows signed owner WORD+0x20;
    negative returns 11. Nonnegative selects global 0x876C50 plus 64B
    per ID, and returns BYTE+0x2B iff the *computed native pointer* is
    nonzero. The caller must establish that pointer computation and the
    exact referenced source bytes; it cannot be inferred from current clubs.
    """
    if type(original_club_word18) is not int or not 0 <= original_club_word18 <= 0xFFFF:
        raise SourceFastViewNativePlayerRosterError("native club WORD+0x18 required")
    if original_club_word18 == 0:
        if any(v is not None for v in (original_62ac80_virtual30_result,
                                     original_62ac80_signed_word20,
                                     original_computed_registry_pointer_nonzero,
                                     original_registry_slot_bytes)):
            raise SourceFastViewNativePlayerRosterError("unreached original mode/registry must not be supplied")
        return SOURCE_FASTVIEW_ROSTER_DEFAULT_OPTION
    if type(original_62ac80_virtual30_result) is not int or not 0 <= original_62ac80_virtual30_result <= 255:
        raise SourceFastViewNativePlayerRosterError("source owner virtual+0x30 byte result required")
    if original_62ac80_virtual30_result != 0:
        if any(v is not None for v in (original_62ac80_signed_word20,
                                     original_computed_registry_pointer_nonzero,
                                     original_registry_slot_bytes)):
            raise SourceFastViewNativePlayerRosterError("unreached native registry fields supplied")
        return SOURCE_FASTVIEW_ROSTER_DEFAULT_OPTION
    if (type(original_62ac80_signed_word20) is not int or
            not -0x8000 <= original_62ac80_signed_word20 <= 0x7FFF):
        raise SourceFastViewNativePlayerRosterError("signed source owner WORD+0x20 required")
    if original_62ac80_signed_word20 < 0:
        if original_computed_registry_pointer_nonzero is not None or original_registry_slot_bytes is not None:
            raise SourceFastViewNativePlayerRosterError("negative original registry index bypasses pointer")
        return SOURCE_FASTVIEW_ROSTER_DEFAULT_OPTION
    if type(original_computed_registry_pointer_nonzero) is not bool:
        raise SourceFastViewNativePlayerRosterError("verified native computed pointer gate required")
    if not original_computed_registry_pointer_nonzero:
        if original_registry_slot_bytes is not None:
            raise SourceFastViewNativePlayerRosterError("native null pointer cannot have source slot bytes")
        return SOURCE_FASTVIEW_ROSTER_DEFAULT_OPTION
    if type(original_registry_slot_bytes) is not bytes or len(original_registry_slot_bytes) < 0x2C:
        raise SourceFastViewNativePlayerRosterError("native registry slot BYTE+0x2B required")
    return original_registry_slot_bytes[0x2B]


SOURCE_FASTVIEW_CLUB_HUMAN_REGISTRY_TEST_VA = 0x4037B0
SOURCE_FASTVIEW_NATIVE_HUMAN_CLUB_LOOP_VA = 0x4139F0
SOURCE_FASTVIEW_NATIVE_HUMAN_LOOKUP_VA = 0x413B40
SOURCE_FASTVIEW_NATIVE_CLUB_COUNTRY_TEST_VA = 0x5337C0
SOURCE_FASTVIEW_NATIVE_COUNTRY_INDEX_LOOKUP_VA = 0x533830
SOURCE_FASTVIEW_NATIVE_SHIPPED_MODE_STUB_VA = 0x6596A0
SOURCE_FASTVIEW_NATIVE_CLUB_MODE_FIELD_VA = 0x533980


def source_fastview_original_human_club_4037b0(
    *, original_club_reference_dword: int,
    original_human_registry_club_ids_in_link_order: tuple[int, ...],
) -> int | None:
    """0x4037B0→0x4139E0→0x4139F0 global human linked-list membership.

    Source iterates global owner 0x874C10+0x9CC, follows node+0x04,
    dereferences each DBRUser+0x5B4 and compares its DWORD+0x04 to
    supplied club object+0x04. Native 0x413B40 returns the first matching
    user from the same list, NOT only the current human manager. Return
    its original list ordinal, or None when no member. Real pointer→ID
    identity and registry contents must come from actual authenticated
    original/port session, not from guessed selected-club defaults.
    """
    if type(original_club_reference_dword) is not int or not 0 <= original_club_reference_dword <= 0xFFFFFFFF:
        raise SourceFastViewNativePlayerRosterError("native source club+0x04 DWORD required")
    if (type(original_human_registry_club_ids_in_link_order) is not tuple
        or len(original_human_registry_club_ids_in_link_order)>6
        or any(type(v) is not int or not 0<=v<=0xFFFFFFFF
               for v in original_human_registry_club_ids_in_link_order)):
        raise SourceFastViewNativePlayerRosterError("qualified original 0..6 human club linked-list IDs required")
    try:
        return original_human_registry_club_ids_in_link_order.index(original_club_reference_dword)
    except ValueError:
        return None


def source_fastview_original_country_header_5337c0(
    *, original_club_record: bytes,
    original_533830_country_indexes_germany_france_england: tuple[int, int, int],
) -> bool:
    """Shipped 0x5337C0 club+0x84 nonzero + three exact country-ID tests.

    0x533830 obtains GLOBAL database indexes for fixed original string
    literals Germany/France/England via the original name registry. It may
    return -1 for an unresolvable name. Original compares the raw DWORD
    value to club+0x14 (even if the lookup returns -1); its 0x6596A0
    mode call is proven to unconditionally return zero in the shipped
    original PE, so the England comparison is reachable. Never substitute
    guessed country-ID constants or the reconstructed league index.
    """
    if type(original_club_record) is not bytes or len(original_club_record)<0x86:
        raise SourceFastViewNativePlayerRosterError("source club+0x84 and country+0x14 required")
    ids=original_533830_country_indexes_germany_france_england
    if (type(ids) is not tuple or len(ids)!=3
        or any(type(i) is not int or not -1<=i<=0x7FFFFFFF for i in ids)):
        raise SourceFastViewNativePlayerRosterError("three qualified native 533830 database country lookup indexes required")
    if unpack_from('<H',original_club_record,0x84)[0] == 0:
        return False
    native_club_country_dword=unpack_from('<I',original_club_record,0x14)[0]
    return any(native_club_country_dword==(i&0xFFFFFFFF) for i in ids)


def source_fastview_original_header_mode_word_533980(*, original_club_record: bytes) -> int:
    """Original 0x6596A0 always eax=0; 0x533980 reads WORD club+0xD8."""
    if type(original_club_record) is not bytes or len(original_club_record)<0xDA:
        raise SourceFastViewNativePlayerRosterError("qualified club record through +0xD9 required")
    return unpack_from('<H',original_club_record,0xD8)[0]
