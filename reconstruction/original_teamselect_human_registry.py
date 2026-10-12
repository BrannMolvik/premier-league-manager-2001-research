"""Source-bounded original TeamSelect registered-user node ownership.

Private original footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
0x412D04 initializes registered-user list +0x9C8 payload-deletion flag to 1.
0x413BB0 appends source-created user nodes; 0x413C60 assigns current index.
0x4D90B6 -> 0x413B80 finds selected club user. 0x413DB0 -> 0x414680
unlinks the node and destroys its payload only if owner+0 != 0.

This is NOT original user creation, staff destruction, shared CRT, GUI,
message handling, or live GameState integration. Caller supplies already
source-qualified user identities and club records.
"""
from __future__ import annotations
from dataclasses import dataclass


class OriginalTeamSelectHumanRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalRegisteredHuman:
    club_id: int
    source_user_token: int

    def __post_init__(self):
        if (type(self.club_id) is not int or self.club_id < 0
                or type(self.source_user_token) is not int
                or self.source_user_token < 0):
            raise OriginalTeamSelectHumanRegistryError(
                "Require source-identified club and already-created user token"
            )


@dataclass(frozen=True)
class OriginalRegisteredHumanRemoval:
    removed_index: int
    removed: OriginalRegisteredHuman
    updated: "OriginalRegisteredHumanRegistry"
    native_node_disposed: bool
    native_user_payload_destructor_called: bool

    @property
    def native_staff_list_payload_deletion_flags(self) -> tuple[int, int, int] | None:
        """Source 0x424FC0 flags for user+0x5B8,+0x5C4,+0x5D0.

        If 0x414680 skips user destructor, this deselection path implies
        no user staff-list destructor. Otherwise 0x425000/0x42500C/
        0x425016 set flags 1,1,0 before 0x4145A0 linked-list release.
        The flags do NOT establish which staff nodes actually exist.
        """
        return (1, 1, 0) if self.native_user_payload_destructor_called else None


@dataclass(frozen=True)
class OriginalRegisteredHumanRegistry:
    records: tuple[OriginalRegisteredHuman, ...] = ()
    current_index: int = 0
    user_list_payload_deletion_flag: int = 1

    def __post_init__(self):
        if (type(self.records) is not tuple
                or len(self.records) > 6
                or any(type(x) is not OriginalRegisteredHuman for x in self.records)
                or len({x.club_id for x in self.records}) != len(self.records)
                or len({x.source_user_token for x in self.records}) != len(self.records)
                or type(self.user_list_payload_deletion_flag) is not int
                or self.user_list_payload_deletion_flag not in (0, 1)
                or type(self.current_index) is not int
                or (self.records and not 0 <= self.current_index < len(self.records))
                or (not self.records and self.current_index not in (-1, 0))):
            raise OriginalTeamSelectHumanRegistryError(
                "Inconsistent original human linked-list projection"
            )

    def register(self, club_id: int, source_user_token: int):
        """Project 0x413BB0 duplicate guard/append without allocating a user."""
        new = OriginalRegisteredHuman(club_id, source_user_token)
        if any(r.club_id == club_id for r in self.records):
            return self, False
        if len(self.records) == 6:
            raise OriginalTeamSelectHumanRegistryError(
                "Original TeamSelect limit is six humans"
            )
        if any(r.source_user_token == source_user_token for r in self.records):
            raise OriginalTeamSelectHumanRegistryError("Native user pointer reused")
        return OriginalRegisteredHumanRegistry(
            self.records + (new,), len(self.records),
            self.user_list_payload_deletion_flag,
        ), True

    def deselect(self, club_id: int) -> OriginalRegisteredHumanRemoval:
        """Project 0x413B80 club match + 0x413DB0 -> 0x414680 unlink.

        The Boolean only indicates the original destructor CALL; none
        of that destructor's transitive user/staff/queue effects are run.
        """
        if type(club_id) is not int:
            raise OriginalTeamSelectHumanRegistryError("Require exact source club ID")
        indices = [i for i, record in enumerate(self.records) if record.club_id == club_id]
        if not indices:
            # Native TeamSelect assumes an actual matching selected club.
            # Fail closed instead of decrementing a non-existent user count.
            raise OriginalTeamSelectHumanRegistryError("Club has no registered human")
        index = indices[0]
        updated = OriginalRegisteredHumanRegistry(
            self.records[:index] + self.records[index + 1:],
            len(self.records) - 2, self.user_list_payload_deletion_flag,
        )
        return OriginalRegisteredHumanRemoval(
            index, self.records[index], updated, True,
            self.user_list_payload_deletion_flag != 0,
        )
