"""Source-qualified portable 606540 human injury notice transaction boundary.

Recreates ONLY the source-proven 606540 -> 7BD564 global pending ->
613EE0 signed due scan -> 5CFA20 -> 413020 eligible first-user route.
Native pointers and native queue node bytes are evidence inputs, NEVER saved.
A source receipt does not mean original Windows binary was executed; the
modern port may record the deterministic projected dispatch but does NOT
claim native heap ownership, native 5CF990 execution or visible PEAMail.
7D7760 player expiry is a DIFFERENT event: due occurrences fail closed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_606540_human_notice import (
    Original606540HumanNoticeReached,
    source_original_606540_human_notice_plan,
)
from original_native_606540_human_mail_route import (
    Original606540HumanDueReached,
    source_original_606540_human_notice_due_to_user,
)
from original_native_613ee0_multi_chain import (
    Original613EE0MultiChainReached,
    source_original_613ee0_multi_chain_pre_callback,
)


class Original606540PortableWorldError(ValueError):
    pass


def _u32(value, name):
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise Original606540PortableWorldError(name + " requires native uint32")
    return value


def _s32(value):
    return value - 0x100000000 if value >= 0x80000000 else value


@dataclass(frozen=True)
class Original606540PortablePending:
    serial: int
    original_player_id: int
    original_constructor: int
    original_class_vtable: int
    original_type: int
    original_creation_manager_key: int
    original_due_day_raw: int


@dataclass(frozen=True)
class Original606540PortableUserNotice:
    serial: int
    original_player_id: int
    original_constructor: int
    original_class_vtable: int
    original_type: int
    recipient_manager_key: int
    original_record_day_raw: int
    # Dynamic name/interpolation, read/unread state and preview are unknown.
    visible_inbox_accepted: bool = False


@dataclass(frozen=True)
class Original606540PortableWorld:
    """Immutable future-saveable original event subset, without PE pointers."""

    next_serial: int = 1
    pending: tuple[Original606540PortablePending, ...] = ()
    user_notices: tuple[Original606540PortableUserNotice, ...] = ()

    def __post_init__(self):
        if type(self.next_serial) is not int or self.next_serial < 1:
            raise Original606540PortableWorldError("Invalid original event serial cursor")
        used = set()
        for item in (*self.pending, *self.user_notices):
            if type(item) not in (Original606540PortablePending,
                                 Original606540PortableUserNotice):
                raise Original606540PortableWorldError("Unknown original notice class")
            if (type(item.serial) is not int or not 0 < item.serial < self.next_serial
                    or item.serial in used):
                raise Original606540PortableWorldError("Duplicate or invalid event serial")
            used.add(item.serial)
            _u32(item.original_due_day_raw if type(item) is Original606540PortablePending
                 else item.original_record_day_raw, "source event date")
            if (type(item.original_player_id) is not int or item.original_player_id < 0
                    or type(item.original_constructor) is not int
                    or item.original_type not in (2, 30, 31)):
                raise Original606540PortableWorldError("Invalid player/constructor/type")
            if type(item) is Original606540PortablePending:
                _u32(item.original_creation_manager_key, "source owner")
            else:
                _u32(item.recipient_manager_key, "source recipient")
                if item.visible_inbox_accepted:
                    raise Original606540PortableWorldError(
                        "No original native GUI acceptance receipt exists")
        if tuple(e.serial for e in self.pending) != tuple(
            sorted(e.serial for e in self.pending)
        ) or tuple(e.serial for e in self.user_notices) != tuple(
            sorted(e.serial for e in self.user_notices)
        ):
            raise Original606540PortableWorldError("Source append order was lost")

    def append_source_constructor(
        self, original_reached: Original606540HumanNoticeReached,
        *, reached_source_club_record: bytes,
        reached_source_club_pointer: int,
    ) -> "Original606540PortableWorld":
        """Qualified constructor source evidence, no claimed native allocation."""
        plan = source_original_606540_human_notice_plan(original_reached)
        owner = original_reached.original_registered_417340_owner_proof
        if (_u32(reached_source_club_pointer, "club pointer")
                != owner.original_source_club_pointer):
            raise Original606540PortableWorldError("Original club owner pointer drift")
        club = reached_source_club_record
        if type(club) is not bytes or len(club) < 0x44:
            raise Original606540PortableWorldError("Original club+40 owner required")
        if unpack_from("<I", club, 4)[0] != owner.original_source_club_owner_key:
            raise Original606540PortableWorldError("Original club+4 identity mismatch")
        # Actual 417270 constructor reads club+40; do not use generic club ID.
        manager_key = unpack_from("<I", club, 0x40)[0]
        from original_native_606540_human_mail_route import _CONSTRUCTORS
        vt = _CONSTRUCTORS.get(plan.original_selected_constructor_address)
        if vt is None or plan.original_notice_envelope_vtable != 0x7BD564:
            raise Original606540PortableWorldError("Unqualified original constructor")
        event = Original606540PortablePending(
            self.next_serial, plan.original_player_id,
            plan.original_selected_constructor_address, vt[0],
            (31, 30, 2)[plan.original_lookup_family],
            manager_key, plan.original_notice_wrapper_date_raw_u32,
        )
        return Original606540PortableWorld(
            self.next_serial+1, (*self.pending, event), self.user_notices
        )

    def apply_original_due_batch(
        self,
        *,
        reached_global_scan: Original613EE0MultiChainReached,
        original_due_notices: tuple[tuple[int, Original606540HumanDueReached], ...],
        registered_manager_keys: tuple[int, ...],
    ) -> "Original606540PortableWorld":
        """Atomic, exact FIFO source projection; all due human nodes required.

        A due 7D7760 player cleanup or unqualified other pending type blocks
        the batch; never mark a user notice delivered while omitting another
        due event. Callback mutation/reentrant 614080 must be cleared in
        the eventual full original-world integration, not faked here.
        """
        scan = source_original_613ee0_multi_chain_pre_callback(reached_global_scan)
        if (type(original_due_notices) is not tuple
                or type(registered_manager_keys) is not tuple
                or len(registered_manager_keys) > 6
                or len(set(registered_manager_keys)) != len(registered_manager_keys)):
            raise Original606540PortableWorldError("Ordered source owners required")
        for key in registered_manager_keys:
            _u32(key, "registered user key")
        due_decisions = tuple(d for d in scan.source_decisions_in_native_order
                              if d.source_virtual10_would_be_called)
        if any(d.event_vtable != 0x7BD564 for d in due_decisions):
            raise Original606540PortableWorldError(
                "Due player 7D7760 cleanup must execute atomically with human notices")
        if len(due_decisions) != len(original_due_notices):
            raise Original606540PortableWorldError(
                "All due global human nodes must be covered in source FIFO order")
        pending_by_serial = {x.serial: x for x in self.pending}
        removed = set()
        new_user = list(self.user_notices)
        for decision, specified in zip(due_decisions, original_due_notices):
            if (type(specified) is not tuple or len(specified) != 2
                    or type(specified[0]) is not int
                    or type(specified[1]) is not Original606540HumanDueReached):
                raise Original606540PortableWorldError("Typed source due receipt required")
            serial, original = specified
            pending = pending_by_serial.get(serial)
            if pending is None or serial in removed:
                raise Original606540PortableWorldError("Unowned or repeated pending identity")
            if (decision.event_pointer != original.original_7bd564_wrapper_pointer
                    or original.original_7bd564_wrapper_before_due
                    != next(n.event_before for n in reached_global_scan.ordered_source_nodes
                            if n.wrapper_pointer == decision.wrapper_pointer)):
                raise Original606540PortableWorldError("Original pending event node identity drift")
            source = source_original_606540_human_notice_due_to_user(original)
            plan = source_original_606540_human_notice_plan(
                original.original_construction_source)
            raw = source.original_source_notice_after_5cfa20
            key = unpack_from("<I", raw, 0x14)[0]
            raw_date = unpack_from("<I", raw, 4)[0]
            if (pending.original_player_id != source.original_player_id
                    or pending.original_constructor != source.original_constructor
                    or pending.original_class_vtable != source.original_concrete_notice_vtable
                    or pending.original_type != source.original_native_type_descriptor
                    or pending.original_creation_manager_key != key
                    or pending.original_due_day_raw != raw_date
                    or plan.original_notice_wrapper_date_raw_u32 != raw_date
                    or source.original_source_current_date_signed32
                    != scan.original_target_signed_day):
                raise Original606540PortableWorldError("Source creation/due owner or date changed")
            user = source.original_413020_qualified_recipient_user_pointer
            if user is not None:
                if key not in registered_manager_keys:
                    raise Original606540PortableWorldError(
                        "Source-matched native recipient missing in live user registry")
                # Source 413020's FIRST matching linked user's club+40 key must
                # equal class descriptor+14 and the exact reached user pointer.
                matching = tuple(n for n in original.original_413020_reached_manager_nodes
                                 if n.original_user_pointer == user)
                if (len(matching) != 1 or
                        unpack_from("<I", matching[0].original_user_context_record, 0x40)[0]
                        != key):
                    raise Original606540PortableWorldError("Registered user pointer/key mismatch")
                new_user.append(Original606540PortableUserNotice(
                    serial, source.original_player_id, source.original_constructor,
                    source.original_concrete_notice_vtable,
                    source.original_native_type_descriptor, key, raw_date,
                ))
            removed.add(serial)
        return Original606540PortableWorld(
            self.next_serial,
            tuple(p for p in self.pending if p.serial not in removed),
            tuple(sorted(new_user, key=lambda p: p.serial)),
        )

    def snapshot(self) -> dict:
        """Private-port JSON surrogate. No binary PE addresses as pointers."""
        self.__post_init__()
        return {"next_serial": self.next_serial,
                "pending": [vars(x).copy() for x in self.pending],
                "user_notices": [vars(x).copy() for x in self.user_notices]}

    @classmethod
    def restore(cls, value: dict | None) -> "Original606540PortableWorld":
        if value is None:
            return cls()
        if type(value) is not dict or set(value) != {
            "next_serial", "pending", "user_notices"
        }:
            raise Original606540PortableWorldError("Invalid source portable event save")
        if type(value["pending"]) is not list or type(value["user_notices"]) is not list:
            raise Original606540PortableWorldError("Source event lists must be ordered")
        from dataclasses import fields
        def decode(records, itemtype):
            names = {x.name for x in fields(itemtype)}
            result = []
            for row in records:
                if type(row) is not dict or set(row) != names or any(
                    type(x) is not int for x in row.values()
                ):
                    raise Original606540PortableWorldError(
                        "Invalid source event field or saved pointer"
                    )
                result.append(itemtype(**row))
            return tuple(result)
        return cls(
            value["next_serial"],
            decode(value["pending"], Original606540PortablePending),
            decode(value["user_notices"], Original606540PortableUserNotice),
        )
