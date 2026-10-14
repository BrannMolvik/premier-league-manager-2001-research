"""Sparse original native 4085D0 player/role and club-quota world sidecar.

Qualified raw owner fields only; no assumptions that modern RuntimePlayer's
generic flags, reserve roles or date represent original native memory.
Snapshots use portable scalar values, never original process addresses.
Original PE provenance SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations

from dataclasses import dataclass,field
from struct import unpack_from


class OriginalNativeWorldStateError(ValueError):
    pass


def _int(value: int, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low<=value<=high:
        raise OriginalNativeWorldStateError(f"qualified native {label} integer out of range")
    return value


def source_native_registered_key(signed_index: int) -> int:
    _int(signed_index,-32768,32767,"registered club signed index")
    # Original 874B94 is ONE fallback owner for every signed negative index.
    return -1 if signed_index<0 else signed_index


@dataclass(frozen=True)
class OriginalNativePlayerStatusWorld:
    original_player_id: int
    original_status_14: int
    original_reserve_selection_174: int
    original_reserve_role_152: int
    original_reserve_aux_153: int
    original_role_object_byte_3: int
    original_role_object_byte_4: int
    original_current_club_index_10: int
    original_registered_club_index_72: int

    def __post_init__(self):
        _int(self.original_player_id,0,65535,"player ID")
        for name in ("original_status_14","original_reserve_selection_174"):
            _int(getattr(self,name),0,0xffffffff,name)
        for name in (
            "original_reserve_role_152","original_reserve_aux_153",
            "original_role_object_byte_3","original_role_object_byte_4",
        ):
            _int(getattr(self,name),0,255,name)
        for name in ("original_current_club_index_10","original_registered_club_index_72"):
            _int(getattr(self,name),-32768,32767,name)

    def array(self) -> list[int]:
        return [
            self.original_player_id,self.original_status_14,
            self.original_reserve_selection_174,self.original_reserve_role_152,
            self.original_reserve_aux_153,self.original_role_object_byte_3,
            self.original_role_object_byte_4,self.original_current_club_index_10,
            self.original_registered_club_index_72,
        ]


def source_native_player_status_world_from_reached(
    *, original_player_record: bytes,
    original_source_role_object_pointer: int,
    original_source_role_object_record: bytes,
    original_mapped_player_id: int,
) -> OriginalNativePlayerStatusWorld:
    p=original_player_record
    obj=original_source_role_object_record
    if type(p) is not bytes or len(p)<0x24c:
        raise OriginalNativeWorldStateError("actual native player through+248 required")
    if type(obj) is not bytes or len(obj)<5:
        raise OriginalNativeWorldStateError("actual native role object through+4 required")
    _int(original_source_role_object_pointer,1,0xffffffff,"role object pointer")
    if unpack_from("<I",p,0x248)[0] != original_source_role_object_pointer:
        raise OriginalNativeWorldStateError("original source role object +248 pointer mismatch")
    pid=unpack_from("<H",p,4)[0]
    if _int(original_mapped_player_id,0,65535,"mapped player")!=pid:
        raise OriginalNativeWorldStateError("independently mapped player ID mismatch")
    return OriginalNativePlayerStatusWorld(
        pid,unpack_from("<I",p,0x14)[0],
        unpack_from("<I",p,0x174)[0],p[0x152],p[0x153],
        obj[3],obj[4],unpack_from("<h",p,0x10)[0],
        unpack_from("<h",p,0x72)[0],
    )


@dataclass
class OriginalNativeStatusWorldState:
    players: dict[int,OriginalNativePlayerStatusWorld] = field(default_factory=dict)
    registered_club_quotas: dict[int,int] = field(default_factory=dict)

    def validate(self) -> None:
        if type(self.players) is not dict or type(self.registered_club_quotas) is not dict:
            raise OriginalNativeWorldStateError("native status world owner maps required")
        for id,record in self.players.items():
            if type(id) is not int or not isinstance(record,OriginalNativePlayerStatusWorld):
                raise OriginalNativeWorldStateError("native status player record type invalid")
            if record.original_player_id!=id:
                raise OriginalNativeWorldStateError("source player owner identity mismatch")
        for club_id,counter in self.registered_club_quotas.items():
            _int(club_id,-1,32767,"registered club canonical key")
            _int(counter,-2147483648,2147483647,"registered club signed quota")

    def snapshot(self) -> dict:
        self.validate()
        return {
            "players":[v.array() for _,v in sorted(self.players.items())],
            "registered_club_quotas":[[k,v] for k,v in sorted(self.registered_club_quotas.items())],
        }

    @classmethod
    def restore(cls, raw: dict | None, valid_player_ids: set[int]) -> "OriginalNativeStatusWorldState":
        if raw is None:
            return cls()
        if (type(raw) is not dict or set(raw)!={"players","registered_club_quotas"}
                or type(raw["players"]) is not list
                or type(raw["registered_club_quotas"]) is not list
                or type(valid_player_ids) is not set):
            raise OriginalNativeWorldStateError("native status world internal save shape invalid")
        players={}
        previous=-1
        for item in raw["players"]:
            if type(item) is not list or len(item)!=9:
                raise OriginalNativeWorldStateError("saved native player status has nine fields")
            entry=OriginalNativePlayerStatusWorld(*item)
            if entry.original_player_id not in valid_player_ids or entry.original_player_id<=previous:
                raise OriginalNativeWorldStateError("missing, duplicated or out-of-order native player")
            players[entry.original_player_id]=entry
            previous=entry.original_player_id
        quotas={}
        previous=-2
        for item in raw["registered_club_quotas"]:
            if type(item) is not list or len(item)!=2:
                raise OriginalNativeWorldStateError("saved registered club quota has two fields")
            key=_int(item[0],-1,32767,"saved club key")
            value=_int(item[1],-2147483648,2147483647,"saved club quota")
            if key<=previous:
                raise OriginalNativeWorldStateError("duplicated/out-of-order registered club quota")
            quotas[key]=value
            previous=key
        state=cls(players,quotas)
        state.validate()
        return state
