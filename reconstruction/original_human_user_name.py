"""Source-bounded single selected DBRUser first/surname and club manager slot.

Private original PE SHA-256: 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
0x426090 initializes the DBRUser name from the PRE-rebind club manager
(or literal John Smith); 0x4261B8 binds a free '!'-slot, and
0x4D0A22..0x4D0A61 later copies edited user strings back into +0x05/+0x25.
This is a source-derived owner only; it does not claim that edit GUI,
multi-human registry, original save format or message preview is restored.
"""
from __future__ import annotations

from dataclasses import dataclass


class OriginalHumanUserNameError(ValueError):
    pass


def _source_string(value: object, label: str) -> str:
    if type(value) is not str or "\x00" in value:
        raise OriginalHumanUserNameError(f"{label} must be a source CP1252 string")
    try:
        encoded = value.encode("cp1252")
    except UnicodeEncodeError as exc:
        raise OriginalHumanUserNameError(f"{label} cannot be represented in CP1252") from exc
    # Native DBRUser+0x05/+0x25 are 0x20-byte name fields. Avoid copying
    # beyond the source field even though old CRT strcpy lacks a safe bound.
    if len(encoded) > 31:
        raise OriginalHumanUserNameError(f"{label} exceeds native 31-byte field")
    return value


@dataclass(frozen=True)
class OriginalHumanUserName:
    """Retained original single-human user, not an AI manager table record."""

    selected_club_id: int
    rebound_manager_slot: int
    first_name: str
    surname: str

    def __post_init__(self) -> None:
        if type(self.selected_club_id) is not int or self.selected_club_id < 0:
            raise OriginalHumanUserNameError("Source selected club must have nonnegative ID")
        if type(self.rebound_manager_slot) is not int or self.rebound_manager_slot < 0:
            raise OriginalHumanUserNameError("Source rebound manager slot must be nonnegative")
        _source_string(self.first_name, "First name")
        _source_string(self.surname, "Surname")

    def source_manager_name(self) -> str:
        """Original 0x613040 uses PE literal '%s %s' after human name lookup."""
        return "%s %s" % (self.first_name, self.surname)

    def snapshot(self) -> dict:
        return {
            "selected_club_id": self.selected_club_id,
            "rebound_manager_slot": self.rebound_manager_slot,
            "first_name": self.first_name,
            "surname": self.surname,
        }

    @classmethod
    def restore(cls, value: object) -> "OriginalHumanUserName":
        expected = {"selected_club_id", "rebound_manager_slot", "first_name", "surname"}
        if type(value) is not dict or set(value) != expected:
            raise OriginalHumanUserNameError("Invalid original human user name snapshot")
        return cls(**value)


def original_fresh_human_name(
    *, club_id: int, rebound_manager_slot: int, clubs, managers
) -> OriginalHumanUserName | None:
    """Source 0x426090 before club+0x40 rebind; return None if unqualified.

    Caller has a single TeamSelect user. A separate original slot search
    0x4151C0 must have identified an unused '!' slot; a legacy AI manager
    fallback is not evidence that native human registration occurred.
    """
    if type(club_id) is not int or type(rebound_manager_slot) is not int:
        return None
    club = clubs.get(club_id)
    slot = managers.get(rebound_manager_slot)
    if club is None or slot is None:
        return None
    slot_name = getattr(slot, "first_name", None)
    if type(slot_name) is not str or not slot_name.startswith("!"):
        return None
    old_index = getattr(club, "manager_id", None)
    if type(old_index) is not int or old_index == rebound_manager_slot:
        return None
    if old_index in (-1, 0xFFFFFFFF):
        first, surname = "John", "Smith"
    else:
        old = managers.get(old_index)
        if old is None:
            return None
        old_club = getattr(old, "club_id", None)
        if type(old_club) is not int:
            return None
        if old_club in (-1, 0xFFFFFFFF):
            first, surname = "John", "Smith"
        else:
            first = getattr(old, "first_name", None)
            surname = getattr(old, "surname", None)
            if type(first) is not str or type(surname) is not str:
                return None
    try:
        return OriginalHumanUserName(club_id, rebound_manager_slot, first, surname)
    except OriginalHumanUserNameError:
        return None
