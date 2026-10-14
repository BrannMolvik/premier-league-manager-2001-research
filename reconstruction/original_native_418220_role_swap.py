"""Original player::0x418220 first/reserve role exchange, source byte projection.

Private original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This is an exact read/write byte projection from reached native records.
No original native allocations, virtual callbacks, GameState writes or UI.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from


class Original418220RoleSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original418220RoleSwapReceipt:
    original_player_id: int
    original_source_role_object_pointer: int
    original_player_after_418220: bytes
    original_source_role_object_after_418220: bytes
    original_former_active_role_code: int
    original_former_active_aux_code: int
    original_former_reserve_role_152: int
    original_former_reserve_aux_153: int
    native_418220_executed: bool = False
    live_game_state_updated: bool = False


def source_original_418220_role_swap_from_reached(
    *, original_player_at_418220: bytes,
    original_source_role_object_pointer: int,
    original_source_role_object_at_418220: bytes,
) -> Original418220RoleSwapReceipt:
    """Source 418220 4EA3C0/D0 getters and 4EA330/350 setters.

    Original role object+3: low5 role; +4 low4 auxiliary.
    Native player+152/+153: saved reserve role/aux bytes.
    Setter 4EA330 changes only low5 of object+3, 4EA350 changes
    only low4 of object+4; then old decoded values are stored as
    entire bytes to native player+152 and +153. Original +174 bit0
    is NOT reset in this function; caller 418180 does that later.
    """
    p=original_player_at_418220
    obj=original_source_role_object_at_418220
    if type(p) is not bytes or len(p)<0x24c:
        raise Original418220RoleSourceError("original source player bytes through+248 required")
    if type(obj) is not bytes or len(obj)<5:
        raise Original418220RoleSourceError("original role object bytes through+4 required")
    ptr=original_source_role_object_pointer
    if type(ptr) is not int or not 0<ptr<=0xffffffff:
        raise Original418220RoleSourceError("original role object nonzero pointer required")
    if unpack_from("<I",p,0x248)[0]!=ptr:
        raise Original418220RoleSourceError("source player+248 role object pointer identity mismatch")
    active=obj[3]&0x1f
    active_aux=obj[4]&0x0f
    reserve=p[0x152]
    reserve_aux=p[0x153]
    changed_role=bytearray(obj)
    changed_player=bytearray(p)
    changed_role[3]=(changed_role[3]&0xe0)|(reserve&0x1f)
    changed_role[4]=(changed_role[4]&0xf0)|(reserve_aux&0x0f)
    changed_player[0x152]=active
    changed_player[0x153]=active_aux
    return Original418220RoleSwapReceipt(
        unpack_from("<H",p,4)[0],ptr,bytes(changed_player),
        bytes(changed_role),active,active_aux,reserve,reserve_aux,
    )
