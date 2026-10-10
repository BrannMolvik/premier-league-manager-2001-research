"""Persistent semantic shadow of the primary ScheduleContainer.

This is intentionally not a gameplay implementation for every competition.
It retains the post-placement/post-shuffle participant graph needed by the
shared 0x615D10 next-team-match lookup used by 0x5127A0.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Callable, Iterable

from competition_schedule import club_refs_conflict
from competition_startup import CupClubRefDescriptor
from competition_state import season_weekday_date


WRAPPER_LINK_CLEAR = "clear"
WRAPPER_LINK_LINKED = "linked"
WRAPPER_LINK_UNKNOWN = "unknown"
WRAPPER_LINK_STATES = frozenset((
    WRAPPER_LINK_CLEAR,
    WRAPPER_LINK_LINKED,
    WRAPPER_LINK_UNKNOWN,
))
NATIVE_MATCH_KINDS = frozenset((
    'fixed_league_match', 'league_match', 'cup_match', 'first_leg_match',
    'second_leg_match', 'replay_match',
))


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
    wrapper_link_state: str = WRAPPER_LINK_CLEAR
    # Only the three 615C50 filter bits, not reconstructed Cup rule flags.
    payload_filter_bits: int | None = None
    side_club_cache: tuple[int | None, int | None] | None = None
    postponed_from_date: date | None = None
    postponement_reason: int | None = None

    def __post_init__(self) -> None:
        if self.wrapper_link_state not in WRAPPER_LINK_STATES:
            raise ValueError("primary schedule wrapper-link state is invalid")
        if self.postponed_from_date is not None and type(self.postponed_from_date) is not date:
            raise ValueError('primary postponed-event parent date is invalid')
        if self.postponed_from_date is not None and (
            type(self.postponement_reason) is not int or self.postponement_reason not in (0, 1, 2)
        ):
            raise ValueError('primary postponed-event reason is invalid')
        if self.postponed_from_date is None and self.postponement_reason is not None:
            raise ValueError('primary root event cannot have a postponement reason')
        if self.payload_filter_bits is not None and (
            type(self.payload_filter_bits) is not int
            or self.payload_filter_bits < 0 or self.payload_filter_bits & ~0x61
        ):
            raise ValueError("primary payload filter bits are invalid")
        if self.side_club_cache is not None and (
            type(self.side_club_cache) is not tuple or len(self.side_club_cache) != 2
            or any(value is not None and (type(value) is not int or value < 0)
                   for value in self.side_club_cache)
            or any(ref.direct_club_id is not None and cache != ref.direct_club_id
                   for ref, cache in zip(self.refs, self.side_club_cache))
        ):
            raise ValueError("primary Side cache is invalid")

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
                    payload_filter_bits=(0 if node.node_kind in NATIVE_MATCH_KINDS else None),
                    side_club_cache=((node.participant_0_ref.direct_club_id,
                                      node.participant_1_ref.direct_club_id)
                                     if node.node_kind in NATIVE_MATCH_KINDS else None),
                )
                for node in bucket
            )
        return cls(days=days)

    def _replace_entry(self, on_date: date, index: int, **values):
        entries = list(self.days[on_date])
        entries[index] = replace(entries[index], **values)
        self.days[on_date] = tuple(entries)
        return entries[index]

    def _entry_index(self, on_date, node_token):
        matches = [i for i, entry in enumerate(self.days.get(on_date, ()))
                   if entry.node_token == node_token]
        if len(matches) != 1:
            raise RuntimeError('Original NEXT event identity is unresolved')
        return matches[0]

    def _replace_payload(self, on_date, index, **values):
        entry = self.days[on_date][index]
        if entry.postponed_from_date is None and entry.wrapper_link_state == WRAPPER_LINK_CLEAR:
            return self._replace_entry(on_date, index, **values)
        # PostponedEvent+18 delegates to the original payload, not a copy.
        for day, entries in tuple(self.days.items()):
            self.days[day] = tuple(replace(item, **values) if item.node_token == entry.node_token
                                   else item for item in entries)
        return self.days[on_date][index]

    def _terminal_event(self, on_date, index):
        visited = set()
        while True:
            entry = self.days[on_date][index]
            if on_date in visited:
                raise RuntimeError('Original NEXT postponed-event cycle')
            visited.add(on_date)
            if entry.wrapper_link_state == WRAPPER_LINK_CLEAR:
                return on_date, index
            children = [(day, i) for day, entries in self.days.items()
                        for i, item in enumerate(entries) if item.node_token == entry.node_token
                        and item.postponed_from_date == on_date]
            if entry.wrapper_link_state != WRAPPER_LINK_LINKED or len(children) != 1:
                raise RuntimeError('Original NEXT terminal wrapper lifecycle is unresolved')
            on_date, index = children[0]

    def resolve_ordinary_side(self, on_date, index, side, resolve_ref,
                              registration_required, *, postpone=None, priority=None):
        """510320 Side cache and native first-peer conflict dispatch.

        Cache publication precedes the recursive 616020 peer query, as in
        4F28A0. Required registration or an absent postponement producer refuses.
        Callers stage this mutable lookup with the rest of the NEXT turn.
        """
        entry = self.days[on_date][index]
        if entry.side_club_cache is None:
            raise RuntimeError('Original NEXT Side cache lifecycle is unresolved')
        cached = entry.side_club_cache[side]
        if cached is not None:
            return cached
        resolved = resolve_ref(entry.refs[side])
        if resolved is None:
            return None
        if registration_required(entry):
            raise RuntimeError('Original NEXT resolved Side registration is not integrated')
        cache = list(entry.side_club_cache)
        cache[side] = int(resolved)
        self._replace_payload(on_date, index, side_club_cache=tuple(cache))
        on_date, index = self._terminal_event(on_date, index)
        entry = self.days[on_date][index]
        # 615F40: same bucket (self skipped), then previous, then next.
        for peer_date in (on_date, on_date - timedelta(days=1),
                          on_date + timedelta(days=1)):
            for original_peer in self.days.get(peer_date, ()):
                peer_index = self._entry_index(peer_date, original_peer.node_token)
                peer = self.days[peer_date][peer_index]
                if peer.payload_filter_bits is None:
                    raise RuntimeError('Original NEXT peer payload flags are unresolved')
                if peer.payload_filter_bits & 0x20:
                    continue
                matches = any(self.resolve_ordinary_side(
                    peer_date, peer_index, peer_side, resolve_ref,
                    registration_required, postpone=postpone,
                    priority=priority) == resolved for peer_side in (0, 1))
                if matches and (peer_date, peer.node_token) != (on_date, entry.node_token):
                    if postpone is None or priority is None:
                        raise RuntimeError('Original NEXT Side conflict requires native postponement: '
                                           f'{on_date} {entry.node_token!r} vs '
                                           f'{peer_date} {peer.node_token!r}')
                    peer = self.days[peer_date][self._entry_index(peer_date, peer.node_token)]
                    own_priority, peer_priority = priority(entry), priority(peer)
                    selected = ((on_date, self._entry_index(on_date, entry.node_token))
                                if peer_priority > own_priority or (
                                    peer_priority == own_priority and peer.payload_filter_bits & 1)
                                else (peer_date, self._entry_index(peer_date, peer.node_token)))
                    postpone(*selected, 0)
                    return int(resolved)
        return int(resolved)

    def ordinary_next_candidate(self, club_id, from_date, resolve_ref,
                                registration_required, *, postpone=None, priority=None,
                                container_end_date=None):
        """615D10/615C50 ordinary manager query; never a display-header lookup."""
        end = container_end_date or max(self.days, default=from_date) + timedelta(days=1)
        on_date = from_date
        while on_date < end:
            for original in self.days.get(on_date, ()):
                index = self._entry_index(on_date, original.node_token)
                entry = self.days[on_date][index]
                if entry.payload_filter_bits is None:
                    raise RuntimeError('Original NEXT payload flags are unresolved')
                if entry.payload_filter_bits & 0x20:
                    continue
                matches = any(self.resolve_ordinary_side(
                    on_date, index, side, resolve_ref, registration_required,
                    postpone=postpone, priority=priority
                ) == club_id for side in (0, 1))
                if not matches:
                    continue
                index = self._entry_index(on_date, original.node_token)
                entry = self.days[on_date][index]
                if entry.wrapper_link_state == WRAPPER_LINK_LINKED:
                    continue
                if entry.wrapper_link_state != WRAPPER_LINK_CLEAR:
                    raise RuntimeError('Original NEXT wrapper lifecycle is unresolved')
                if entry.payload_filter_bits & 0x41:
                    continue
                # 514520 invokes both sides, even when the manager matched side 0.
                for side in (0, 1):
                    index = self._entry_index(on_date, original.node_token)
                    if self.days[on_date][index].wrapper_link_state == WRAPPER_LINK_LINKED:
                        break
                    self.resolve_ordinary_side(on_date, index, side, resolve_ref,
                                               registration_required, postpone=postpone,
                                               priority=priority)
                entry = self.days[on_date][self._entry_index(on_date, original.node_token)]
                if entry.wrapper_link_state == WRAPPER_LINK_CLEAR:
                    return on_date, entry
            on_date += timedelta(days=1)
        return None

    def prepare_ordinary_day(self, on_date, resolve_ref, registration_required, *,
                             postpone=None, priority=None):
        """4A7280: current 615C10 readiness, then tomorrow's 616600/514520."""
        for current in (on_date, on_date + timedelta(days=1)):
            for original in self.days.get(current, ()):
                index = self._entry_index(current, original.node_token)
                entry = self.days[current][index]
                if entry.payload_filter_bits is None:
                    raise RuntimeError('Original NEXT current-day payload flags are unresolved')
                if entry.wrapper_link_state == WRAPPER_LINK_UNKNOWN:
                    raise RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')
                if current != on_date:
                    # 514520 skips linked/20/40 and rechecks the link between Sides.
                    if entry.wrapper_link_state == WRAPPER_LINK_LINKED or entry.payload_filter_bits & 0x60:
                        continue
                    self.resolve_ordinary_side(current, index, 0, resolve_ref,
                        registration_required, postpone=postpone, priority=priority)
                    index = self._entry_index(current, original.node_token)
                    if self.days[current][index].wrapper_link_state == WRAPPER_LINK_CLEAR:
                        self.resolve_ordinary_side(current, index, 1, resolve_ref,
                            registration_required, postpone=postpone, priority=priority)
                    continue
                if entry.payload_filter_bits & 1:
                    continue
                ready = False
                if not entry.payload_filter_bits & 0x20:
                    ready = self.resolve_ordinary_side(current, index, 0, resolve_ref,
                        registration_required, postpone=postpone, priority=priority) is not None
                    if ready:
                        index = self._entry_index(current, original.node_token)
                        ready = self.resolve_ordinary_side(current, index, 1, resolve_ref,
                            registration_required, postpone=postpone, priority=priority) is not None
                prior_complete = True
                if ready and entry.node_kind == 'second_leg_match':
                    # The recovered constructor links +54 to this emitted first leg.
                    prior = [item for bucket in self.days.values() for item in bucket
                             if item.node_kind == 'first_leg_match'
                             and item.postponed_from_date is None
                             and item.competition_id == entry.competition_id
                             and item.competition_context == entry.competition_context
                             and item.node_token == ('cup_first_leg',) + entry.node_token[1:]]
                    if len(prior) != 1 or prior[0].payload_filter_bits is None:
                        raise RuntimeError('Original NEXT prior-leg lifecycle is unresolved')
                    prior_complete = bool(prior[0].payload_filter_bits & 1)
                if not ready or not prior_complete:
                    if postpone is None:
                        raise RuntimeError('Original NEXT unready current-day event requires postponement: '
                                           f'{current} {entry.node_token!r}')
                    postpone(current, self._entry_index(current, original.node_token), 1)

    def retain_ordinary_completion(self, on_date, node_token):
        """Retain 511381's bit 0 after actual calculation, never from a score lookup."""
        matches = [i for i, entry in enumerate(self.days.get(on_date, ()))
                   if entry.node_token == tuple(node_token)]
        if len(matches) != 1:
            raise RuntimeError('Original NEXT calculator event owner is unresolved')
        index = matches[0]
        entry = self.days[on_date][index]
        if entry.wrapper_link_state != WRAPPER_LINK_CLEAR or entry.payload_filter_bits is None:
            raise RuntimeError('Original NEXT calculator flags/link are unresolved')
        if entry.payload_filter_bits & 0x61:
            raise RuntimeError('Original NEXT calculator event is not eligible')
        self._replace_payload(on_date, index,
                              payload_filter_bits=entry.payload_filter_bits | 1)

    def postpone_ordinary_event(self, on_date, index, *, current_date, container_end_date,
                               resolve_ref, registration_required, postpone, priority, reason):
        """510BA0/615A60: linked old event, delegated payload, +7/head insertion."""
        original = self.days[on_date][index]
        if original.wrapper_link_state == WRAPPER_LINK_LINKED:
            return None
        if original.wrapper_link_state != WRAPPER_LINK_CLEAR or original.payload_filter_bits is None:
            raise RuntimeError('Original NEXT postponement guard is unresolved')
        if original.payload_filter_bits & 0x40:
            return None
        self._replace_entry(on_date, index, wrapper_link_state=WRAPPER_LINK_LINKED)
        candidate = max(on_date + timedelta(days=7), current_date + timedelta(days=1))
        while candidate < container_end_date:
            conflict = None
            for peer_date in (candidate - timedelta(days=1), candidate, candidate + timedelta(days=1)):
                for peer_original in self.days.get(peer_date, ()):
                    peer_index = self._entry_index(peer_date, peer_original.node_token)
                    peer = self.days[peer_date][peer_index]
                    if peer.wrapper_link_state == WRAPPER_LINK_LINKED:
                        continue
                    if peer.wrapper_link_state != WRAPPER_LINK_CLEAR or peer.payload_filter_bits is None:
                        raise RuntimeError('Original NEXT insertion peer lifecycle is unresolved')
                    if peer.payload_filter_bits & 0x40:
                        continue
                    for peer_side in (0, 1):
                        for own_side in (0, 1):
                            # 510A80 invokes candidate equality against each existing Side.
                            own_index = self._entry_index(on_date, original.node_token)
                            payload = self.days[on_date][own_index]
                            if payload.side_club_cache is None:
                                raise RuntimeError('Original NEXT insertion Side cache is unresolved')
                            own_value = payload.side_club_cache[own_side]
                            if own_value is None:
                                # New terminal wrapper still has +10=-1: 510320 skips615F40.
                                own_value = resolve_ref(payload.refs[own_side])
                                if own_value is not None:
                                    if registration_required(payload):
                                        raise RuntimeError('Original NEXT resolved Side registration is not integrated')
                                    cache = list(payload.side_club_cache)
                                    cache[own_side] = int(own_value)
                                    self._replace_payload(on_date, own_index, side_club_cache=tuple(cache))
                            peer_index = self._entry_index(peer_date, peer_original.node_token)
                            peer_value = self.resolve_ordinary_side(
                                peer_date, peer_index, peer_side, resolve_ref, registration_required,
                                postpone=postpone, priority=priority)
                            own_ref, peer_ref = original.refs[own_side], peer_original.refs[peer_side]
                            matches = (own_value == peer_value if own_value is not None
                                       and peer_value is not None else own_value is None
                                       and peer_value is None and club_refs_conflict(own_ref, peer_ref))
                            if matches:
                                conflict = peer_date
                                break
                        if conflict is not None:
                            break
                    if conflict is not None:
                        break
                if conflict is not None:
                    break
            if conflict is None:
                source_index = self._entry_index(on_date, original.node_token)
                payload = self.days[on_date][source_index]
                wrapper = replace(payload, wrapper_link_state=WRAPPER_LINK_CLEAR,
                                  postponed_from_date=on_date, postponement_reason=reason)
                self.days[candidate] = (wrapper,) + self.days.get(candidate, ())
                return candidate
            candidate = conflict + timedelta(days=2)
        raise RuntimeError('Original NEXT postponement exceeds retained calendar')

    @staticmethod
    def _dynamic_node_conflicts_entry(node, entry: PrimaryScheduleShadowEntry) -> bool:
        return any(
            club_refs_conflict(existing_ref, candidate_ref)
            for existing_ref in entry.refs
            for candidate_ref in (
                node.participant_0_ref,
                node.participant_1_ref,
            )
        )

    def first_dynamic_conflict_near(
        self,
        node,
        center_date: date,
    ) -> date | None:
        """Reproduce the 0x615890 three-day probe for a runtime-created match."""

        center_date = date.fromisoformat(center_date.isoformat())
        for on_date in (
            center_date - timedelta(days=1),
            center_date,
            center_date + timedelta(days=1),
        ):
            for entry in self.days.get(on_date, ()):
                if self._dynamic_node_conflicts_entry(node, entry):
                    return on_date
        return None

    def choose_dynamic_insertion_date(
        self,
        node,
        *,
        requested_date: date,
        current_date: date,
    ) -> date:
        """Reproduce runtime ScheduleContainer::insert at 0x615A60.

        0x615A60 clamps the requested relative day to at least current+1,
        probes candidate-1/candidate/candidate+1 through 0x615890, and when
        a conflicting match is found resumes from conflict+2. The accepted
        node is then head-inserted into that already-shuffled day bucket.
        """

        candidate = max(
            date.fromisoformat(requested_date.isoformat()),
            date.fromisoformat(current_date.isoformat()) + timedelta(days=1),
        )
        while True:
            conflict = self.first_dynamic_conflict_near(node, candidate)
            if conflict is None:
                return candidate
            candidate = conflict + timedelta(days=2)

    def insert_dynamic_node(
        self,
        node,
        *,
        on_date: date,
    ) -> PrimaryScheduleShadowEntry:
        """Head-insert a runtime-created match into one live primary day.

        Runtime 0x615A60 writes the new match's next pointer to the prior bucket
        head and then stores the new match as the head. choose_dynamic_insertion_date()
        owns the preceding conflict displacement; this method applies only the
        final linked-list insertion order.
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
            payload_filter_bits=(0 if node.node_kind in NATIVE_MATCH_KINDS else None),
            side_club_cache=((node.participant_0_ref.direct_club_id,
                              node.participant_1_ref.direct_club_id)
                             if node.node_kind in NATIVE_MATCH_KINDS else None),
        )
        self.days[on_date] = (entry,) + tuple(self.days.get(on_date, ()))
        return entry

    def invalidate_unmodelled_wrapper_links(self) -> None:
        """Downgrade source-known clear wrapper links after an unknown reschedule pass.

        Recovery 401 source-closes fresh direct wrappers as clear, but native
        post-start producers at 0x4A801F/0x5E3C34 can later create +0x08 links.
        Until those producers are represented, a day-advance boundary cannot
        preserve a positive claim that any previously clear wrapper stayed clear.
        Explicit linked state remains linked.
        """
        self.days = {
            on_date: tuple(
                entry if entry.wrapper_link_state == WRAPPER_LINK_LINKED
                else replace(entry, wrapper_link_state=WRAPPER_LINK_UNKNOWN)
                for entry in entries
            )
            for on_date, entries in self.days.items()
        }

    def direct_fixed_league_header_candidate(
        self,
        club_id: int,
        from_date: date,
        *,
        played_fixture_ids: Iterable[int] = (),
    ) -> tuple[date, PrimaryScheduleShadowEntry] | None:
        """Bounded 0x615D10/0x615C50 projection for fresh direct LeagueMatch.

        Only the Recovery-401 source-closed subset is accepted. Exact
        date-forward bucket order and head-to-tail entry order are preserved.
        A relevant symbolic/unsupported/unknown entry fails closed rather than
        being skipped. Native linked wrappers and already-played fixed League
        matches are skipped by the recovered selector predicates.
        """
        club_id = int(club_id)
        played = {int(value) for value in played_fixture_ids}
        for on_date in sorted(value for value in self.days if value >= from_date):
            for entry in self.days[on_date]:
                direct = tuple(ref.direct_club_id for ref in entry.refs)
                if any(value is None for value in direct):
                    if any(club_id in possible for possible in entry.candidate_sets):
                        return None
                    continue
                participants = tuple(int(value) for value in direct)
                if club_id not in participants:
                    continue

                if (
                    entry.node_kind != "fixed_league_match"
                    or entry.competition_id != 0
                    or entry.competition_context != 0
                ):
                    return None
                if len(entry.node_token) != 4:
                    return None
                try:
                    fixture_id = int(entry.node_token[-1])
                except (TypeError, ValueError):
                    return None
                if fixture_id in played:
                    continue
                if entry.wrapper_link_state == WRAPPER_LINK_LINKED:
                    continue
                if entry.wrapper_link_state != WRAPPER_LINK_CLEAR:
                    return None
                return on_date, entry
        return None

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
                    "wrapper_link_state": entry.wrapper_link_state,
                    "payload_filter_bits": entry.payload_filter_bits,
                    "side_club_cache": (None if entry.side_club_cache is None
                                        else list(entry.side_club_cache)),
                    "postponed_from_date": (None if entry.postponed_from_date is None
                                            else entry.postponed_from_date.isoformat()),
                    "postponement_reason": entry.postponement_reason,
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

        state = cls(
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
                        wrapper_link_state=str(
                            raw.get("wrapper_link_state", WRAPPER_LINK_UNKNOWN)
                        ),
                        payload_filter_bits=raw.get('payload_filter_bits'),
                        side_club_cache=(None if raw.get('side_club_cache') is None
                                         else tuple(raw['side_club_cache'])),
                        postponed_from_date=(None if raw.get('postponed_from_date') is None
                                             else date.fromisoformat(raw['postponed_from_date'])),
                        postponement_reason=raw.get('postponement_reason'),
                    )
                    for raw in entries
                )
                for on_date, entries in value.items()
            }
        )
        children = set()
        for on_date, entries in state.days.items():
            for entry in entries:
                if entry.postponed_from_date is None:
                    continue
                parent_key = (entry.postponed_from_date, entry.node_token)
                if parent_key in children:
                    raise ValueError('primary postponed-event parent has multiple children')
                children.add(parent_key)
                parents = [item for item in state.days.get(entry.postponed_from_date, ())
                           if item.node_token == entry.node_token]
                if len(parents) != 1 or entry.postponed_from_date >= on_date:
                    raise ValueError('primary postponed-event parent is invalid')
                parent = parents[0]
                if parent.wrapper_link_state != WRAPPER_LINK_LINKED or (
                    parent.refs, parent.side_club_cache, parent.payload_filter_bits,
                    parent.node_kind, parent.competition_id, parent.competition_context
                ) != (
                    entry.refs, entry.side_club_cache, entry.payload_filter_bits,
                    entry.node_kind, entry.competition_id, entry.competition_context
                ):
                    raise ValueError('primary postponed-event delegated payload is inconsistent')
        return state
