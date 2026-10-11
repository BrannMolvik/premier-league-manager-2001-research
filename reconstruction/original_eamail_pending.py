"""Source-typed MPMEAMail pending envelopes, not the visible PEAMail Inbox.

Verified original footballmanager.exe SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
0x41B679 creates next-native-day PlayerAskTransferList MPMEAMail envelopes;
0x613EC0 inserts separate queue nodes at 0x947AA8.
0x613EE0 visits each due envelope exactly once with removal flag 1;
0x5CFA20 gates on record virtual +0x3C, stamps scheduled date, transfers
the record pointer to 0x413020's per-user mailbox and clears envelope+8.
Other MPM event families and native PE pointer ownership are not modeled.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from match_postmatch import PlayerTransferRequest
from original_eamail_mailbox import (
    OriginalDeliveredEAMailboxes,
    source_player_ask_transfer_list_record_ready,
)


class OriginalPendingEAMSourceError(ValueError):
    """The original 0x947AA8 pending-event identity is not qualified."""


@dataclass(frozen=True)
class OriginalPendingTransferEnvelope:
    """One stable modern identity for a source-backed original 12-byte envelope."""

    sequence: int
    request: PlayerTransferRequest

    def __post_init__(self) -> None:
        if type(self.sequence) is not int or self.sequence <= 0:
            raise OriginalPendingEAMSourceError("Pending envelope sequence must be positive")
        if type(self.request) is not PlayerTransferRequest:
            raise OriginalPendingEAMSourceError("Only source-backed transfer EAM event supported")
        if self.request.event_class != "EAMPlayerAskTransferListsub":
            raise OriginalPendingEAMSourceError("Unverified original MPM event class")
        if (self.request.recipient_manager_key is None
                or self.request.sender_club_id is None):
            raise OriginalPendingEAMSourceError("Producer-time native recipient and sender required")
        if self.request.due_on != self.request.queued_on + timedelta(days=1):
            raise OriginalPendingEAMSourceError("Original 0x41B681 next-day envelope required")

    @property
    def identity(self) -> str:
        """Durable modern event surrogate, not a native PE pointer or row index."""
        return f"MPMEAMail/PlayerAskTransferList/{self.sequence}"


@dataclass
class OriginalPendingTransferEAMQueue:
    """Append-ordered original EAM transfer subset; distinct from delivered mail."""

    entries: list[OriginalPendingTransferEnvelope] = field(default_factory=list)
    next_sequence: int = 1

    def __post_init__(self) -> None:
        if type(self.entries) is not list or type(self.next_sequence) is not int or self.next_sequence < 1:
            raise OriginalPendingEAMSourceError("Malformed source pending event queue")
        prior = 0
        for entry in self.entries:
            if (type(entry) is not OriginalPendingTransferEnvelope
                    or entry.sequence <= prior or entry.sequence >= self.next_sequence):
                raise OriginalPendingEAMSourceError("Duplicate, unsequenced or invalid event node")
            prior = entry.sequence

    def append_original_transfer(self, request: PlayerTransferRequest) -> OriginalPendingTransferEnvelope:
        """Source 0x41B679..0x41B6A6: record -> envelope -> 0x613EC0 list node."""
        event = OriginalPendingTransferEnvelope(self.next_sequence, request)
        self.entries.append(event)
        self.next_sequence += 1
        return event

    def remove_player_linked(self, player_id: int) -> None:
        """Bounded part of original 0x5CE460 player-linked queue purge."""
        if type(player_id) is not int or player_id < 0:
            raise OriginalPendingEAMSourceError("Source player ID required")
        self.entries[:] = [e for e in self.entries if e.request.player_id != player_id]

    def process_original_due(
        self, at_date: date, delivered: OriginalDeliveredEAMailboxes
    ) -> tuple[str, ...]:
        """0x613EE0(flag=1): deliver qualified record, then consume due envelope.

        The original queue's removal is independent of whether a record is
        delivered. An unregistered human mailbox is not fabricated.
        Call only at the native NEXT/PResults event-processing boundary,
        under the caller's transaction/rollback protection.
        """
        if type(at_date) is not date or type(delivered) is not OriginalDeliveredEAMailboxes:
            raise OriginalPendingEAMSourceError("Source current date and delivered owner required")
        processed: list[str] = []
        remaining: list[OriginalPendingTransferEnvelope] = []
        for event in self.entries:
            if event.request.due_on > at_date:
                remaining.append(event)
                continue
            delivered.deliver_source_ready_transfer_request(
                event.request,
                pending_identity=event.identity,
                at_date=at_date,
                original_record_ready=source_player_ask_transfer_list_record_ready(
                    event.request.event_class
                ),
            )
            # 0x613F12..0x613F1C removes the due 0x947AA8 node even when
            # 0x5CFA20's record virtual rejects (that case belongs to other
            # classes, not the verified always-ready transfer subtype).
            processed.append(event.identity)
        self.entries = remaining
        return tuple(processed)

    def snapshot(self) -> dict:
        """Modern internal-save surrogate; no proprietary original save format."""
        self.__post_init__()
        return {
            "next_sequence": self.next_sequence,
            "entries": [
                {
                    "sequence": event.sequence,
                    "player_id": event.request.player_id,
                    "queued_on": event.request.queued_on.isoformat(),
                    "due_on": event.request.due_on.isoformat(),
                    "recipient_manager_key": event.request.recipient_manager_key,
                    "sender_club_id": event.request.sender_club_id,
                }
                for event in self.entries
            ],
        }

    @classmethod
    def restore(cls, source: dict | None) -> "OriginalPendingTransferEAMQueue":
        """Legacy saves do not retroactively create source-qualified events."""
        if source is None:
            return cls()
        if type(source) is not dict or set(source) != {"entries", "next_sequence"}:
            raise OriginalPendingEAMSourceError("Invalid original EAM pending save owner")
        if type(source["entries"]) is not list:
            raise OriginalPendingEAMSourceError("Pending source events must be ordered")
        events: list[OriginalPendingTransferEnvelope] = []
        for row in source["entries"]:
            if type(row) is not dict or set(row) != {
                "sequence", "player_id", "queued_on", "due_on",
                "recipient_manager_key", "sender_club_id"
            }:
                raise OriginalPendingEAMSourceError("Invalid serialized pending source node")
            try:
                request = PlayerTransferRequest(
                    player_id=row["player_id"],
                    queued_on=date.fromisoformat(row["queued_on"]),
                    due_on=date.fromisoformat(row["due_on"]),
                    recipient_manager_key=row["recipient_manager_key"],
                    sender_club_id=row["sender_club_id"],
                )
            except (TypeError, ValueError, KeyError) as exc:
                raise OriginalPendingEAMSourceError("Invalid source EAM record") from exc
            events.append(OriginalPendingTransferEnvelope(row["sequence"], request))
        return cls(entries=events, next_sequence=source["next_sequence"])
