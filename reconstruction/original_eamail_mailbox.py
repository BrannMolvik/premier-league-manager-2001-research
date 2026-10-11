"""Source-bounded original EAMail delivered owner, distinct from pending MPM.

The original DBRUser+0x6B4 mailbox is an append-only ordered list of
12-byte nodes (0x424E2E, 0x617D70), not the global 0x947AA8 pending event
owner or PEAMail's separately sorted display array. This models only source
qualified EAMPlayerAskTransferListsub delivery after the *caller* has proved
the authentic native due-event dispatch. The original per-class readiness and
retention virtuals are now independently traced, but do not establish
NEXT/PResults queue execution, an original pointer/node serializer, native
message body or a playable Inbox screen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from match_postmatch import PlayerTransferRequest


# Independently traced native MSVC RTTI / PE vtable on the original
# 4,714,541-byte executable (SHA-256 833bf95e...5838b7cc3).
# See research/GATE13_EAM_TRANSFER_READINESS_RETENTION_SOURCE_RECOVERY527.md.
EAM_PLAYER_ASK_TRANSFER_LIST_CLASS = "EAMPlayerAskTransferListsub"
EAM_PLAYER_ASK_TRANSFER_LIST_TYPEDESC_VA = 0x818F40
EAM_PLAYER_ASK_TRANSFER_LIST_COL_VA = 0x7DF7C8
EAM_PLAYER_ASK_TRANSFER_LIST_VFTABLE_VA = 0x7BDB1C
EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VIRTUAL_OFFSET = 0x3C
EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VA = 0x4093E0
EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VIRTUAL_OFFSET = 0x40
EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VA = 0x470CE0
EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_NATIVE_DATE_UNITS = 0x16D


def source_player_ask_transfer_list_record_ready(original_class: str) -> bool:
    """Class-exact native +0x3C = 0x4093E0: mov eax,1; ret.

    This callback does NOT confirm a scheduled MPM envelope is due or has
    been visited by the original 0x613EE0 dispatcher. It is not a license to
    create Inbox rows from unprocessed pending requests.
    """
    if original_class != EAM_PLAYER_ASK_TRANSFER_LIST_CLASS:
        raise OriginalEAMailOwnerError(
            "Only verified EAMPlayerAskTransferListsub native readiness is supported"
        )
    return True


class OriginalEAMailOwnerError(ValueError):
    """Native mailbox recipient, event or persistence contract not satisfied."""


def _source_index(value: object, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 0x7FFFFFFF:
        raise OriginalEAMailOwnerError(f"{label} must be a nonnegative native index")
    return value


@dataclass(frozen=True)
class OriginalDeliveredEAMail:
    """One owned list node, using *internal* stable serial, not a PE pointer."""

    node_serial: int
    recipient_manager_key: int
    pending_identity: str
    event_class: str
    record_date: date
    player_id: int
    sender_club_id: int
    native_status_decoded: bool = False
    original_screen_rendered: bool = False

    def __post_init__(self) -> None:
        if type(self.node_serial) is not int or self.node_serial < 1:
            raise OriginalEAMailOwnerError("Delivered list node serial must be positive")
        _source_index(self.recipient_manager_key, "recipient key")
        _source_index(self.player_id, "player ID")
        _source_index(self.sender_club_id, "sender club ID")
        if type(self.pending_identity) is not str or not self.pending_identity:
            raise OriginalEAMailOwnerError("Source pending event identity is required")
        if self.event_class != "EAMPlayerAskTransferListsub":
            raise OriginalEAMailOwnerError(
                "Only original source-qualified PlayerAskTransferList route is supported"
            )
        if type(self.record_date) is not date:
            raise OriginalEAMailOwnerError("Source envelope date must be an original date")
        if (type(self.native_status_decoded) is not bool
                or type(self.original_screen_rendered) is not bool
                or self.native_status_decoded or self.original_screen_rendered):
            raise OriginalEAMailOwnerError(
                "Delivered source record cannot claim unknown status or native GUI"
            )


@dataclass
class OriginalDeliveredEAMailboxes:
    """Per-registered-user delivered list, independent of pending and sorting."""

    registered_manager_keys: tuple[int, ...] = ()
    mailboxes: dict[int, list[OriginalDeliveredEAMail]] = field(default_factory=dict)
    next_node_serial: int = 1

    def __post_init__(self) -> None:
        if type(self.registered_manager_keys) is not tuple or (
            len(self.registered_manager_keys) > 6
        ):
            raise OriginalEAMailOwnerError("Original DBRUser registry supports at most six")
        if len(set(self.registered_manager_keys)) != len(self.registered_manager_keys):
            raise OriginalEAMailOwnerError("Duplicate registered mailbox manager key")
        for key in self.registered_manager_keys:
            _source_index(key, "registered manager key")
        if type(self.mailboxes) is not dict or set(self.mailboxes) != set(
            self.registered_manager_keys
        ):
            raise OriginalEAMailOwnerError("Each original user owns exactly one mailbox")
        if type(self.next_node_serial) is not int or self.next_node_serial < 1:
            raise OriginalEAMailOwnerError("Invalid next internal list node serial")
        seen_serials: set[int] = set()
        for manager_key, records in self.mailboxes.items():
            if type(records) is not list:
                raise OriginalEAMailOwnerError("Mailbox node owner must be an ordered list")
            seen_events: set[str] = set()
            previous_serial = 0
            for record in records:
                if (type(record) is not OriginalDeliveredEAMail
                        or record.recipient_manager_key != manager_key
                        or record.node_serial in seen_serials
                        or record.node_serial <= previous_serial
                        or record.node_serial >= self.next_node_serial
                        or record.pending_identity in seen_events):
                    raise OriginalEAMailOwnerError(
                        "Invalid, duplicated or misrouted native mailbox node"
                    )
                seen_serials.add(record.node_serial)
                seen_events.add(record.pending_identity)
                previous_serial = record.node_serial

    def register_source_user(self, manager_key: int) -> None:
        """0x424E2E: construct an empty user+0x6B4 owner (not an inbox row)."""
        _source_index(manager_key, "source registered manager key")
        if manager_key in self.mailboxes:
            raise OriginalEAMailOwnerError("Original mailbox user is already registered")
        if len(self.registered_manager_keys) >= 6:
            raise OriginalEAMailOwnerError("Maximum six original registered users")
        self.registered_manager_keys += (manager_key,)
        self.mailboxes[manager_key] = []

    def delivered_for_manager(self, manager_key: int) -> tuple[OriginalDeliveredEAMail, ...]:
        """Read owned append order; PEAMail display sorting is a separate owner."""
        _source_index(manager_key, "source recipient manager key")
        if manager_key not in self.mailboxes:
            raise OriginalEAMailOwnerError("Manager has no registered source mailbox")
        return tuple(self.mailboxes[manager_key])

    def deliver_source_ready_transfer_request(
        self,
        request: PlayerTransferRequest,
        *,
        pending_identity: str,
        at_date: date,
        original_record_ready: bool | None,
    ) -> OriginalDeliveredEAMail | None:
        """Explicit MPMEAMail::0x5CFA20 branch, not a daily/GUI auto-delivery.

        original_record_ready MUST come from the original EAM class virtual
        +0x3C contract. Its verified constant-true result can be obtained via
        source_player_ask_transfer_list_record_ready(request.event_class).
        False skips append. None/unknown still refuses any promotion, because
        this method must never run without a proven native due-event caller.
        The call MUST be made by the authentic due-event dispatcher; this
        method deliberately does not add itself to NEXT.
        """
        if type(request) is not PlayerTransferRequest:
            raise OriginalEAMailOwnerError("Unsupported original pending event type")
        if type(at_date) is not date:
            raise OriginalEAMailOwnerError("Native due-processing date is required")
        if type(pending_identity) is not str or not pending_identity:
            raise OriginalEAMailOwnerError("Stable source event identity is required")
        if type(original_record_ready) is not bool:
            raise OriginalEAMailOwnerError(
                "Original per-record +0x3C readiness is still unknown"
            )
        if at_date < request.due_on:
            raise OriginalEAMailOwnerError("Native event+0x04 is not yet due")
        if not original_record_ready:
            return None
        manager_key = request.recipient_manager_key
        if manager_key is None or request.sender_club_id is None:
            raise OriginalEAMailOwnerError(
                "Native recipient/sender source context was not captured at production"
            )
        # Original 0x413020 compares effective DBRClub+0x40 to each registered
        # DBRUser. Do not use an immutable imported AI manager_id or broadcast.
        if manager_key not in self.mailboxes:
            return None
        if any(row.pending_identity == pending_identity
               for row in self.mailboxes[manager_key]):
            raise OriginalEAMailOwnerError(
                "One source event must not be delivered twice to one user"
            )
        record = OriginalDeliveredEAMail(
            node_serial=self.next_node_serial,
            recipient_manager_key=manager_key,
            pending_identity=pending_identity,
            event_class=request.event_class,
            record_date=request.due_on,
            player_id=request.player_id,
            sender_club_id=request.sender_club_id,
        )
        self.mailboxes[manager_key].append(record)
        self.next_node_serial += 1
        return record

    def snapshot(self) -> dict:
        """Internal compatibility save only, never original binary save bytes."""
        self.__post_init__()
        return {
            "registered_manager_keys": list(self.registered_manager_keys),
            "next_node_serial": self.next_node_serial,
            "mailboxes": [
                {
                    "manager_key": key,
                    "records": [
                        {
                            "node_serial": row.node_serial,
                            "pending_identity": row.pending_identity,
                            "event_class": row.event_class,
                            "record_date": row.record_date.isoformat(),
                            "player_id": row.player_id,
                            "sender_club_id": row.sender_club_id,
                        }
                        for row in self.mailboxes[key]
                    ],
                }
                for key in self.registered_manager_keys
            ],
        }

    @classmethod
    def restore(cls, value: dict | None) -> "OriginalDeliveredEAMailboxes":
        """Absence in older snapshots means empty/unregistered, not delivered."""
        if value is None:
            return cls()
        if type(value) is not dict or set(value) != {
            "registered_manager_keys", "next_node_serial", "mailboxes"
        }:
            raise OriginalEAMailOwnerError("Invalid modern mailbox save owner")
        keys = value["registered_manager_keys"]
        rows = value["mailboxes"]
        if type(keys) is not list or type(rows) is not list:
            raise OriginalEAMailOwnerError("Modern mailbox registry must be lists")
        for key in keys:
            _source_index(key, "saved registered manager key")
        if len(set(keys)) != len(keys):
            raise OriginalEAMailOwnerError("Duplicate saved original manager key")
        mailbox = cls(
            registered_manager_keys=tuple(keys),
            mailboxes={key: [] for key in keys},
            next_node_serial=value["next_node_serial"],
        )
        if len(rows) != len(keys):
            raise OriginalEAMailOwnerError("Missing mailbox owner in saved user registry")
        for expected, entry in zip(keys, rows):
            if (type(entry) is not dict
                    or set(entry) != {"manager_key", "records"}
                    or type(entry["manager_key"]) is not int
                    or entry["manager_key"] != expected
                    or type(entry["records"]) is not list):
                raise OriginalEAMailOwnerError("Invalid saved per-user mailbox order")
            for source in entry["records"]:
                if type(source) is not dict or set(source) != {
                    "node_serial", "pending_identity", "event_class",
                    "record_date", "player_id", "sender_club_id"
                }:
                    raise OriginalEAMailOwnerError("Invalid saved original EAM record")
                mailbox.mailboxes[expected].append(OriginalDeliveredEAMail(
                    node_serial=source["node_serial"],
                    recipient_manager_key=expected,
                    pending_identity=source["pending_identity"],
                    event_class=source["event_class"],
                    record_date=date.fromisoformat(source["record_date"]),
                    player_id=source["player_id"],
                    sender_club_id=source["sender_club_id"],
                ))
        mailbox.__post_init__()
        return mailbox


_SOURCE_KNOWN_RETENTION_OFFSETS = {
    # Native +0x40 directly resolves to 0x470CE0; checked anew on original PE.
    EAM_PLAYER_ASK_TRANSFER_LIST_CLASS:
        EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_NATIVE_DATE_UNITS,
    "EAMChairSeasonTicketssub": 365,  # +0x40 = 0x470CE0
    "EAMChairSeasonTicketSetsub": 21,   # +0x40 = 0x538530
}


def source_known_eam_record_retained(
    original_class: str, *, source_record_day: int, source_current_day: int
) -> bool:
    """Source numeric 0x9847FC date-units only; NOT Python calendar days."""
    if type(original_class) is not str or (
        original_class not in _SOURCE_KNOWN_RETENTION_OFFSETS
    ):
        raise OriginalEAMailOwnerError(
            "No original +0x40 retention period qualified for this EAM class"
        )
    if (type(source_record_day) is not int or type(source_current_day) is not int
            or source_record_day < 0 or source_current_day < 0):
        raise OriginalEAMailOwnerError("Original retention needs native date-unit integers")
    return source_current_day <= (
        source_record_day + _SOURCE_KNOWN_RETENTION_OFFSETS[original_class]
    )
