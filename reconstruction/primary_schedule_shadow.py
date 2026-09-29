"""Persistent semantic shadow of the primary ScheduleContainer.

This is intentionally not a gameplay implementation for every competition.
It retains the post-placement/post-shuffle participant graph needed by the
shared 0x615D10 next-team-match lookup used by 0x5127A0.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Iterable

from competition_startup import CupClubRefDescriptor
from competition_state import season_weekday_date


class PrimaryScheduleResolutionPending(RuntimeError):
    """An earlier symbolic primary match could still contain the target club."""

    def __init__(self, club_id: int, on_date: date):
        self.club_id = int(club_id)
        self.on_date = on_date
        super().__init__(
            f"primary next-match lookup for club {self.club_id} is unresolved "
            f"from {self.on_date.isoformat()}"
        )


@dataclass(frozen=True)
class PrimaryScheduleShadowEntry:
    node_kind: str
    competition_id: int
    competition_context: int
    node_token: tuple
    participant_0_ref: CupClubRefDescriptor
    participant_1_ref: CupClubRefDescriptor
    participant_0_candidates: frozenset[int]
    participant_1_candidates: frozenset[int]

    @property
    def refs(self) -> tuple[CupClubRefDescriptor, CupClubRefDescriptor]:
        return self.participant_0_ref, self.participant_1_ref

    @property
    def candidate_sets(self) -> tuple[frozenset[int], frozenset[int]]:
        return self.participant_0_candidates, self.participant_1_candidates


@dataclass
class PrimaryScheduleShadowState:
    days: dict[date, tuple[PrimaryScheduleShadowEntry, ...]]

    @classmethod
    def from_primary_schedule_buckets(
        cls,
        buckets: Iterable[Iterable[object]],
        *,
        season_year: int,
    ) -> "PrimaryScheduleShadowState":
        bucket_list = tuple(tuple(bucket) for bucket in buckets)
        all_nodes = tuple(node for bucket in bucket_list for node in bucket)
        by_token = {
            tuple(node.node_token): node
            for node in all_nodes
            if getattr(node, "node_token", None)
        }

        competition_nodes: dict[tuple[int, int], list[object]] = {}
        for node in all_nodes:
            competition_nodes.setdefault(
                (int(node.competition_id), int(node.competition_context)),
                [],
            ).append(node)

        candidates: dict[tuple, frozenset[int]] = {}

        def ref_key(ref: CupClubRefDescriptor) -> tuple:
            return (
                int(ref.type_code),
                int(ref.selector),
                None if ref.direct_club_id is None else int(ref.direct_club_id),
                None if ref.competition_id is None else int(ref.competition_id),
                int(ref.competition_context),
                None if ref.reference_token is None else tuple(ref.reference_token),
            )

        def current_ref_candidates(ref: CupClubRefDescriptor) -> frozenset[int]:
            if ref.direct_club_id is not None:
                return frozenset((int(ref.direct_club_id),))
            return candidates.get(ref_key(ref), frozenset())

        # Fixed-point candidate propagation. Type 1 inherits the source match's
        # two possible participants. Types 2/3/4 identify a position inside a
        # source competition/context; for candidate membership, every club that
        # can participate in that source runtime is conservatively possible.
        changed = True
        while changed:
            changed = False
            for node in all_nodes:
                for ref in (node.participant_0_ref, node.participant_1_ref):
                    key = ref_key(ref)
                    if ref.direct_club_id is not None:
                        value = frozenset((int(ref.direct_club_id),))
                    elif int(ref.type_code) == 1 and ref.reference_token is not None:
                        source = by_token.get(tuple(ref.reference_token))
                        if source is None:
                            value = frozenset()
                        else:
                            value = frozenset().union(
                                current_ref_candidates(source.participant_0_ref),
                                current_ref_candidates(source.participant_1_ref),
                            )
                    elif (
                        int(ref.type_code) in (2, 3, 4)
                        and ref.competition_id is not None
                    ):
                        source_nodes = competition_nodes.get(
                            (
                                int(ref.competition_id),
                                int(ref.competition_context),
                            ),
                            (),
                        )
                        value = frozenset().union(
                            *(
                                frozenset().union(
                                    current_ref_candidates(source.participant_0_ref),
                                    current_ref_candidates(source.participant_1_ref),
                                )
                                for source in source_nodes
                            )
                        ) if source_nodes else frozenset()
                    else:
                        value = frozenset()

                    old = candidates.get(key, frozenset())
                    merged = old | value
                    if merged != old:
                        candidates[key] = merged
                        changed = True

        anchor = season_weekday_date(int(season_year), 0, 1)
        days: dict[date, tuple[PrimaryScheduleShadowEntry, ...]] = {}
        for bucket_index, bucket in enumerate(bucket_list):
            if not bucket:
                continue
            on_date = anchor + timedelta(days=int(bucket_index))
            days[on_date] = tuple(
                PrimaryScheduleShadowEntry(
                    node_kind=str(node.node_kind),
                    competition_id=int(node.competition_id),
                    competition_context=int(node.competition_context),
                    node_token=tuple(node.node_token),
                    participant_0_ref=node.participant_0_ref,
                    participant_1_ref=node.participant_1_ref,
                    participant_0_candidates=current_ref_candidates(
                        node.participant_0_ref
                    ),
                    participant_1_candidates=current_ref_candidates(
                        node.participant_1_ref
                    ),
                )
                for node in bucket
            )
        return cls(days=days)

    def insert_dynamic_node(
        self,
        node,
        *,
        on_date: date,
    ) -> PrimaryScheduleShadowEntry:
        """Insert a runtime-created match into the live primary shadow.

        FA Cup Replay objects are inserted after startup. Their participants
        are already direct resolved clubs, so no fixed-point propagation is
        required. Preserve 0x615950 head-insertion order within the date.
        """
        def candidates(ref: CupClubRefDescriptor) -> frozenset[int]:
            if ref.direct_club_id is None:
                return frozenset()
            return frozenset((int(ref.direct_club_id),))

        entry = PrimaryScheduleShadowEntry(
            node_kind=str(node.node_kind),
            competition_id=int(node.competition_id),
            competition_context=int(node.competition_context),
            node_token=tuple(node.node_token),
            participant_0_ref=node.participant_0_ref,
            participant_1_ref=node.participant_1_ref,
            participant_0_candidates=candidates(node.participant_0_ref),
            participant_1_candidates=candidates(node.participant_1_ref),
        )
        self.days[on_date] = (entry,) + tuple(self.days.get(on_date, ()))
        return entry

    def next_match_date(
        self,
        club_id: int,
        after_date: date,
        resolve_ref: Callable[[CupClubRefDescriptor], int | None],
    ) -> date | None:
        """Reproduce the safe date-level result of 0x615D10.

        0x5127A0 starts at current relative day + 1. For each later bucket,
        a definitively resolved participant equal to the team proves that date.
        If no participant resolves to the club but an unresolved ClubRef's
        startup candidate set still contains it, the exact next date is not
        yet knowable and this method raises rather than skipping that match.
        """
        club_id = int(club_id)
        for on_date in sorted(value for value in self.days if value > after_date):
            uncertain = False
            for entry in self.days[on_date]:
                for ref, possible in zip(entry.refs, entry.candidate_sets):
                    resolved = resolve_ref(ref)
                    if resolved is not None:
                        if int(resolved) == club_id:
                            return on_date
                        continue
                    if club_id in possible:
                        uncertain = True
            if uncertain:
                raise PrimaryScheduleResolutionPending(club_id, on_date)
        return None

    def snapshot(self) -> dict:
        def snap_ref(ref: CupClubRefDescriptor) -> dict:
            return {
                "type_code": int(ref.type_code),
                "selector": int(ref.selector),
                "direct_club_id": (
                    None if ref.direct_club_id is None else int(ref.direct_club_id)
                ),
                "competition_id": (
                    None if ref.competition_id is None else int(ref.competition_id)
                ),
                "competition_context": int(ref.competition_context),
                "reference_token": (
                    None
                    if ref.reference_token is None
                    else list(ref.reference_token)
                ),
            }

        return {
            on_date.isoformat(): [
                {
                    "node_kind": entry.node_kind,
                    "competition_id": entry.competition_id,
                    "competition_context": entry.competition_context,
                    "node_token": list(entry.node_token),
                    "participant_0_ref": snap_ref(entry.participant_0_ref),
                    "participant_1_ref": snap_ref(entry.participant_1_ref),
                    "participant_0_candidates": sorted(entry.participant_0_candidates),
                    "participant_1_candidates": sorted(entry.participant_1_candidates),
                }
                for entry in entries
            ]
            for on_date, entries in sorted(self.days.items())
        }

    @classmethod
    def restore(cls, value: dict) -> "PrimaryScheduleShadowState":
        def tup(value):
            if isinstance(value, list):
                return tuple(tup(item) for item in value)
            return value

        def restore_ref(raw: dict) -> CupClubRefDescriptor:
            return CupClubRefDescriptor(
                type_code=int(raw["type_code"]),
                selector=int(raw["selector"]),
                direct_club_id=(
                    None
                    if raw.get("direct_club_id") is None
                    else int(raw["direct_club_id"])
                ),
                competition_id=(
                    None
                    if raw.get("competition_id") is None
                    else int(raw["competition_id"])
                ),
                competition_context=int(raw.get("competition_context", 0)),
                reference_token=(
                    None
                    if raw.get("reference_token") is None
                    else tup(raw["reference_token"])
                ),
            )

        return cls(
            days={
                date.fromisoformat(on_date): tuple(
                    PrimaryScheduleShadowEntry(
                        node_kind=str(raw["node_kind"]),
                        competition_id=int(raw["competition_id"]),
                        competition_context=int(raw["competition_context"]),
                        node_token=tup(raw["node_token"]),
                        participant_0_ref=restore_ref(raw["participant_0_ref"]),
                        participant_1_ref=restore_ref(raw["participant_1_ref"]),
                        participant_0_candidates=frozenset(
                            int(v) for v in raw["participant_0_candidates"]
                        ),
                        participant_1_candidates=frozenset(
                            int(v) for v in raw["participant_1_candidates"]
                        ),
                    )
                    for raw in entries
                )
                for on_date, entries in value.items()
            }
        )
