from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Protocol, Sequence

from match_events import ChanceRecord, IncidentKind, IncidentRecord, SubstitutionRecord
from match_performance import target_match_performance_rating
from match_injury_persistence import generate_persistent_match_injury
from match_simulation import NormalMatchResult, PreparedMatchSide


DEFAULT_FORM_CHANGE_PROB = 5
DEFAULT_IN_FORM_CHANGE_PROB = 20
DEFAULT_OUT_OF_FORM_CHANGE_PROB = 20
DEFAULT_FORM_INCREASE_PROB = 50

DEFAULT_GOOD_LEADERSHIP = 25
DEFAULT_UNHAPPY_LOST_MATCH = 7
DEFAULT_UNHAPPY_WON_MATCH = 10
DEFAULT_UNHAPPY_NOT_PLAYED = 8
DEFAULT_MAXIMUM_MORALE = 100
DEFAULT_LOAN_MORALE = 10
DEFAULT_SIGNED_NEW_CONTRACT_MORALE = 30
DEFAULT_DANGER_MORALE_LEVEL = 15
DEFAULT_CHANCE_ASK_FOR_TRANSFER = 30


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class MutablePostMatchPlayer(Protocol):
    condition: int
    form_state: int
    injured: bool

    def latest_match_performance(self) -> int: ...
    def append_match_performance(self, value: int) -> int: ...


class MutablePostMatchMoralePlayer(Protocol):
    index: int
    morale: int
    form_state: int
    injured: bool
    suspended: bool
    selection_excluded: bool
    date_of_birth: date | None
    current_raw: Sequence[int]
    transfer_listed: bool
    wanted: bool


class MutableLeagueDisciplinePlayer(Protocol):
    suspended: bool
    discipline_yellow_total: int
    discipline_yellow_cycle: int
    suspension_matches_remaining: int
    suspension_effective_date: date | None


@dataclass(frozen=True)
class MoraleSettings:
    """Shipped DBRPlayer morale tuning for 0x41BA80 and 0x41BB10."""

    good_leadership: int = DEFAULT_GOOD_LEADERSHIP
    lost_match: int = DEFAULT_UNHAPPY_LOST_MATCH
    won_match: int = DEFAULT_UNHAPPY_WON_MATCH
    not_played: int = DEFAULT_UNHAPPY_NOT_PLAYED
    maximum: int = DEFAULT_MAXIMUM_MORALE
    loan: int = DEFAULT_LOAN_MORALE
    signed_new_contract: int = DEFAULT_SIGNED_NEW_CONTRACT_MORALE
    danger_morale_level: int = DEFAULT_DANGER_MORALE_LEVEL
    chance_ask_for_transfer: int = DEFAULT_CHANCE_ASK_FOR_TRANSFER

    def __post_init__(self) -> None:
        for name in (
            "good_leadership",
            "lost_match",
            "won_match",
            "not_played",
            "maximum",
            "loan",
            "signed_new_contract",
            "danger_morale_level",
        ):
            value = int(getattr(self, name))
            if not 0 <= value <= 255:
                raise ValueError(name + " must fit the original unsigned byte")
        if int(self.chance_ask_for_transfer) <= 0:
            raise ValueError("chance_ask_for_transfer must be positive")


@dataclass(frozen=True)
class PlayerTransferRequest:
    """Delayed MPMEAMail created by the low-morale 0x41B580 path."""

    player_id: int
    queued_on: date
    due_on: date

    @property
    def event_class(self) -> str:
        return "EAMPlayerAskTransferListsub"

    @property
    def original_key(self) -> str:
        return "PlayerAskTransferList"

    @property
    def accepted_action_class(self) -> str:
        return "EAMAcceptTransferRequestsub"

    @property
    def refused_action_class(self) -> str:
        return "EAMRefuseTransferRequestsub"


@dataclass(frozen=True)
class FormTransitionSettings:
    """Shipped defaults loaded for DBRPlayer Form updater 0x41B870."""

    form_change_prob: int = DEFAULT_FORM_CHANGE_PROB
    in_form_change_prob: int = DEFAULT_IN_FORM_CHANGE_PROB
    out_of_form_change_prob: int = DEFAULT_OUT_OF_FORM_CHANGE_PROB
    form_increase_prob: int = DEFAULT_FORM_INCREASE_PROB

    def __post_init__(self) -> None:
        for name in (
            "form_change_prob",
            "in_form_change_prob",
            "out_of_form_change_prob",
            "form_increase_prob",
        ):
            value = int(getattr(self, name))
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be in 0..100")


def update_post_match_form(
    form_state: int,
    rng: BoundedRng,
    settings: FormTransitionSettings = FormTransitionSettings(),
) -> int:
    """Exact 0x41B870 five-state post-match Form transition.

    The first RNG(100) uses a state-dependent trigger probability. A failed
    trigger returns immediately and consumes no second draw. A successful
    trigger consumes RNG(100) against FormIncreaseProb; increase/decrease is
    clamped at the 0/4 state boundaries exactly as in the executable.
    """
    state = int(form_state)
    if not 0 <= state <= 4:
        raise ValueError("form_state must be in 0..4")

    if state <= 1:
        trigger = int(settings.out_of_form_change_prob)
    elif state == 2:
        trigger = int(settings.form_change_prob)
    else:
        trigger = int(settings.in_form_change_prob)

    if rng.randbelow(100) >= trigger:
        return state

    if rng.randbelow(100) < int(settings.form_increase_prob):
        return min(4, state + 1)
    return max(0, state - 1)


def decrease_player_morale(
    morale: int,
    base_amount: int,
    age: int,
    leadership: int,
    rng: BoundedRng,
    settings: MoraleSettings = MoraleSettings(),
) -> int:
    """Exact DBRPlayer::0x41BA80 clamped morale decrease."""
    current = int(morale) & 0xFF
    modifier = -1
    if int(leadership) >= int(settings.good_leadership):
        modifier -= 2
    if int(age) > 15:
        modifier -= 1
    if int(age) < 11:
        modifier -= 1
    amount = int(base_amount) + int(rng.randbelow(2)) + modifier
    if amount <= 0:
        return current
    return max(0, current - amount)


def increase_player_morale(
    morale: int,
    base_amount: int,
    age: int,
    leadership: int,
    rng: BoundedRng,
    settings: MoraleSettings = MoraleSettings(),
) -> int:
    """Exact DBRPlayer::0x41BB10 morale increase capped at MaximumMorale."""
    current = int(morale) & 0xFF
    modifier = 1 if int(leadership) >= int(settings.good_leadership) else 0
    modifier = modifier * 2 + (1 if int(age) > 15 else 0)
    if int(age) < 11:
        modifier += 1
    amount = int(base_amount) + int(rng.randbelow(2)) + modifier + 1
    return min(int(settings.maximum), current + amount)


def apply_signed_contract_finalizer_morale(
    player,
    on_date: date,
    rng: BoundedRng,
    settings: MoraleSettings = MoraleSettings(),
) -> int:
    """Replay the trailing morale/latch slice of DBRPlayer::0x419210.

    Direct canonical-executable inspection proves 0x419210 calls
    0x41BB10(SignedNewContactMorale) first and only then clears the
    DBRPlayer+0x164 contract-renewal-suggestion latch. Callers are responsible
    for the earlier contract/status/event mutations that converge on this
    common finalizer.
    """
    age = player.age(on_date)
    if age is None:
        raise ValueError(f"player {int(player.index)} has no usable age")
    current_raw = tuple(int(value) for value in player.current_raw)
    if len(current_raw) <= 15:
        raise ValueError(f"player {int(player.index)} has no leadership skill")
    player.morale = increase_player_morale(
        int(player.morale),
        int(settings.signed_new_contract),
        int(age),
        int(current_raw[15]),
        rng,
        settings,
    )
    player.contract_renewal_suggestion_pending = False
    return int(player.morale)


def _post_match_age(player: MutablePostMatchMoralePlayer, on_date: date) -> int:
    dob = player.date_of_birth
    if dob is None:
        raise ValueError("post-match morale requires a date of birth")
    if on_date < dob:
        raise ValueError("fixture date precedes player date of birth")
    return int(on_date.year) - int(dob.year) - (
        (int(on_date.month), int(on_date.day))
        < (int(dob.month), int(dob.day))
    )


def _post_match_leadership(player: MutablePostMatchMoralePlayer) -> int:
    raw = tuple(int(value) for value in player.current_raw)
    if len(raw) <= 15:
        raise ValueError("post-match morale requires current skill index 15")
    return raw[15]


def _post_match_unavailable(player: MutablePostMatchMoralePlayer) -> bool:
    return bool(player.injured or player.suspended or player.selection_excluded)


def maybe_queue_player_transfer_request(
    player: MutablePostMatchMoralePlayer,
    fixture_date: date,
    rng: BoundedRng,
    *,
    club_user_controlled: bool,
    active_club_user_controlled: bool,
    request_sink: Callable[[PlayerTransferRequest], None] | None,
    settings: MoraleSettings = MoraleSettings(),
) -> bool:
    """Replay DBRPlayer::0x41B580 without inventing UI-side behavior.

    The status duplicate gate is deliberately after RNG(ChanceAskForTransfer),
    matching the canonical executable. A successful trigger queues only the
    source-backed next-day MPMEAMail payload; it does not transfer-list the
    player until the later accepted response is applied.
    """
    if not bool(club_user_controlled) or not bool(active_club_user_controlled):
        return False
    if int(player.morale) >= int(settings.danger_morale_level):
        return False

    if int(rng.randbelow(int(settings.chance_ask_for_transfer))) != 2:
        return False

    # 0x41B7B0: bit 8 Transfer listed, then bit 10 Wanted. This gate is after
    # the trigger draw, so a blocked low-morale player has already advanced RNG.
    if bool(player.transfer_listed) or bool(player.wanted):
        return False

    if request_sink is None:
        return False
    request_sink(
        PlayerTransferRequest(
            player_id=int(player.index),
            queued_on=fixture_date,
            due_on=fixture_date + timedelta(days=1),
        )
    )
    return True


def apply_player_transfer_request_response(
    player: MutablePostMatchMoralePlayer,
    *,
    accept: bool,
) -> None:
    """Apply the direct EAMAccept/RefuseTransferRequest player-state slice.

    Acceptance reaches 0x41B530 -> 0x420A10 and sets Transfer-listed bit 8,
    then Wanted bit 10. Refusal does not mutate morale or these status bits.
    The original 0x420A10 transfer-value cache is not duplicated here because
    the modern runtime resolves transfer value live through the already-mapped
    0x4205A0 equivalent.
    """
    if bool(accept):
        player.transfer_listed = True
        player.wanted = True


def persist_premier_league_morale_and_form(
    roster: Sequence[MutablePostMatchMoralePlayer],
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchMoralePlayer],
    result: NormalMatchResult,
    fixture_date: date,
    rng: BoundedRng,
    *,
    morale_settings: MoraleSettings = MoraleSettings(),
    form_settings: FormTransitionSettings = FormTransitionSettings(),
    club_user_controlled: bool = False,
    active_club_user_controlled: Callable[
        [MutablePostMatchMoralePlayer], bool
    ] | None = None,
    transfer_request_sink: Callable[[PlayerTransferRequest], None] | None = None,
) -> frozenset[int]:
    """Replay detailed 0x404CE0 roster-order morale, Form and danger morale.

    Appeared players execute loss or win morale first and then 0x41B870 Form
    immediately. Eligible non-appeared players execute RNG(10); values below
    four apply the not-played morale decrease. Unavailable non-appeared players
    consume no not-played RNG.

    For a human-controlled club, the same roster iteration then invokes the
    recovered 0x41B580 low-morale request path for that player. Its RNG(30)
    therefore remains interleaved after that player's ordinary morale/Form
    handling rather than becoming a separate whole-roster phase.
    """
    participants = tuple(runtime_participants)
    prepared = tuple(side.players)
    if len(prepared) != len(participants):
        raise ValueError(
            "runtime participant count must match prepared participant count"
        )

    appeared_local = appeared_player_indices(side, result)
    appeared_ids: set[int] = set()
    for local_index in appeared_local:
        if not 0 <= int(local_index) < len(participants):
            raise IndexError("appeared player index outside participant array")
        appeared_ids.add(int(participants[int(local_index)].index))

    score0, score1 = result.score
    own_score, opponent_score = (
        (score0, score1) if int(side.side) == 0 else (score1, score0)
    )
    won = int(own_score) > int(opponent_score)
    lost = int(own_score) < int(opponent_score)

    for player in roster:
        player_id = int(player.index)
        if player_id in appeared_ids:
            age = _post_match_age(player, fixture_date)
            leadership = _post_match_leadership(player)
            if lost:
                player.morale = decrease_player_morale(
                    int(player.morale),
                    int(morale_settings.lost_match),
                    age,
                    leadership,
                    rng,
                    morale_settings,
                )
            if won:
                player.morale = increase_player_morale(
                    int(player.morale),
                    int(morale_settings.won_match),
                    age,
                    leadership,
                    rng,
                    morale_settings,
                )
            player.form_state = update_post_match_form(
                int(player.form_state),
                rng,
                form_settings,
            )
        elif not _post_match_unavailable(player):
            if int(rng.randbelow(10)) < 4:
                player.morale = decrease_player_morale(
                    int(player.morale),
                    int(morale_settings.not_played),
                    _post_match_age(player, fixture_date),
                    _post_match_leadership(player),
                    rng,
                    morale_settings,
                )

        active_controlled = (
            bool(active_club_user_controlled(player))
            if active_club_user_controlled is not None
            else bool(club_user_controlled)
        )
        maybe_queue_player_transfer_request(
            player,
            fixture_date,
            rng,
            club_user_controlled=bool(club_user_controlled),
            active_club_user_controlled=active_controlled,
            request_sink=transfer_request_sink,
            settings=morale_settings,
        )

    return frozenset(appeared_ids)

def appeared_player_indices(
    side: PreparedMatchSide,
    result: NormalMatchResult,
) -> frozenset[int]:
    """Return side-local players who appeared, matching the post-match scope.

    Every original starter counts as an appearance. A bench player joins the
    appeared set when a type-10 substitution record names them as incoming.
    """
    appeared = {int(index) for index in side.starting_player_indices}
    side_id = int(side.side)

    for timed in result.events:
        event = timed.event
        if (
            isinstance(event, SubstitutionRecord)
            and int(event.player_side) == side_id
        ):
            appeared.add(int(event.incoming_player_index))

    return frozenset(appeared)


@dataclass(frozen=True)
class PostMatchPersistenceSummary:
    appeared_player_indices: frozenset[int]
    injured_player_indices: frozenset[int]


def sync_post_match_conditions(
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchPlayer],
) -> None:
    """Copy calculator Condition back before post-match injury finalization."""
    prepared = tuple(side.players)
    runtime = tuple(runtime_participants)
    if len(prepared) != len(runtime):
        raise ValueError(
            "runtime participant count must match prepared participant count"
        )
    for local_index, player in enumerate(prepared):
        if int(player.player_index) != local_index:
            raise ValueError(
                "prepared participants must use contiguous side-local indices"
            )
        runtime[local_index].condition = int(player.condition)


def persist_match_performance_history(
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchPlayer],
    result: NormalMatchResult,
    shared_rng: BoundedRng,
    match_engine_rng: BoundedRng,
) -> tuple[int, ...]:
    """Compute and append exact 0x6309D0 -> 0x630FC0 performance ratings.

    Only players who appeared are processed, matching the original +0x18F
    active/appearance guard. Ratings are computed in participant-array order.
    Goal-family +0x40/+0x44 counters are reconstructed only from non-own goals:
    primary attribution is ChanceRecord.player_index and the separately mapped
    secondary attribution is ChanceRecord.secondary_player_index.
    """
    runtime = tuple(runtime_participants)
    prepared = tuple(side.players)
    if len(prepared) != len(runtime):
        raise ValueError(
            "runtime participant count must match prepared participant count"
        )

    side_id = int(side.side)
    appeared = appeared_player_indices(side, result)
    primary: dict[int, int] = {}
    secondary: dict[int, int] = {}
    booked: set[int] = set()
    sent_off: set[int] = set()

    for timed in result.events:
        event = timed.event
        if isinstance(event, ChanceRecord):
            if not event.is_goal or event.side_inversion:
                continue
            if int(event.player_side) == side_id:
                index = int(event.player_index)
                primary[index] = primary.get(index, 0) + 1
            if (
                event.secondary_player_side is not None
                and int(event.secondary_player_side) == side_id
            ):
                index = int(event.secondary_player_index)
                secondary[index] = secondary.get(index, 0) + 1
        elif isinstance(event, IncidentRecord) and int(event.player_side) == side_id:
            index = int(event.player_index)
            if event.kind is IncidentKind.BOOKED:
                booked.add(index)
            elif event.kind is IncidentKind.SENT_OFF:
                sent_off.add(index)

    score0, score1 = result.score
    own_score, opponent_score = (
        (score0, score1) if side_id == 0 else (score1, score0)
    )

    ratings: list[int] = []
    for local_index, player in enumerate(runtime):
        if local_index not in appeared:
            continue
        prepared_player = prepared[local_index]
        if int(prepared_player.player_index) != local_index:
            raise ValueError(
                "prepared participants must use contiguous side-local indices"
            )
        rating = target_match_performance_rating(
            current_role=int(prepared_player.current_position),
            own_score=own_score,
            opponent_score=opponent_score,
            primary_goal_count=primary.get(local_index, 0),
            secondary_goal_count=secondary.get(local_index, 0),
            booked=local_index in booked,
            sent_off=local_index in sent_off,
            form_state=int(player.form_state),
            previous_rating=int(player.latest_match_performance()),
            shared_rng=shared_rng,
            match_engine_rng=match_engine_rng,
        )
        player.append_match_performance(rating)
        ratings.append(int(rating))

    return tuple(ratings)


def persist_post_match_form(
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchPlayer],
    result: NormalMatchResult,
    rng: BoundedRng,
    *,
    form_settings: FormTransitionSettings = FormTransitionSettings(),
) -> frozenset[int]:
    """Run only the later 0x41B870 Form pass for players who appeared."""
    runtime = tuple(runtime_participants)
    if len(side.players) != len(runtime):
        raise ValueError(
            "runtime participant count must match prepared participant count"
        )
    appeared = appeared_player_indices(side, result)
    for local_index, player in enumerate(runtime):
        if local_index in appeared:
            player.form_state = update_post_match_form(
                int(player.form_state),
                rng,
                form_settings,
            )
    return appeared


@dataclass(frozen=True)
class PremierLeagueIncidentPersistenceSummary:
    discipline: LeagueDisciplineSummary
    injured_player_indices: frozenset[int]


def persist_premier_league_match_incidents(
    roster: Sequence[MutablePostMatchPlayer],
    participants: Sequence[MutablePostMatchPlayer],
    side: int,
    result: NormalMatchResult,
    fixture_date: date,
    next_fixture_date: date | None,
    rng: BoundedRng,
    *,
    user_controlled: bool = False,
) -> PremierLeagueIncidentPersistenceSummary:
    """Exact 0x5127A0 League card/injury interleaving for one team.

    Existing bans are served for the whole roster first. The participant loop
    then processes each player's cards and immediately creates that player's
    persistent injury object before moving to the next participant. This
    preserves red-card RNG(3) versus injury-generator RNG ordering. Finally,
    the suspended bit is refreshed against the club's own next fixture.

    Calculator Condition must already have been synchronized to ``participants``
    before this function is called, matching the original in-place DBRPlayer
    calculator mutations.
    """
    side = int(side)
    if side not in (0, 1):
        raise ValueError("side must be 0 or 1")

    roster_tuple = tuple(roster)
    participant_tuple = tuple(participants)
    served = sum(
        int(serve_league_suspension_after_fixture(player, fixture_date))
        for player in roster_tuple
    )

    bookings: dict[int, int] = {}
    dismissals: dict[int, int] = {}
    injuries: set[int] = set()
    for timed in result.events:
        event = timed.event
        if not isinstance(event, IncidentRecord) or int(event.player_side) != side:
            continue
        local_index = int(event.player_index)
        if event.kind is IncidentKind.BOOKED:
            bookings[local_index] = bookings.get(local_index, 0) + 1
        elif event.kind is IncidentKind.SENT_OFF:
            dismissals[local_index] = dismissals.get(local_index, 0) + 1
        elif event.kind is IncidentKind.INJURED:
            injuries.add(local_index)

    persisted_injuries: set[int] = set()
    for local_index, player in enumerate(participant_tuple):
        apply_league_match_discipline(
            player,
            bookings.get(local_index, 0),
            dismissals.get(local_index, 0),
            fixture_date,
            rng,
        )
        if local_index in injuries:
            generated = generate_persistent_match_injury(
                player,
                roster_tuple,
                fixture_date,
                rng,
                user_controlled=bool(user_controlled),
            )
            if generated is not None:
                persisted_injuries.add(local_index)

    suspended_count = sum(
        int(refresh_league_suspension_for_next_fixture(player, next_fixture_date))
        for player in roster_tuple
    )

    discipline = LeagueDisciplineSummary(
        served_player_count=served,
        booked_player_indices=frozenset(bookings),
        sent_off_player_indices=frozenset(dismissals),
        suspended_for_next_fixture_count=suspended_count,
    )
    return PremierLeagueIncidentPersistenceSummary(
        discipline=discipline,
        injured_player_indices=frozenset(persisted_injuries),
    )

def persist_post_match_side(
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchPlayer],
    result: NormalMatchResult,
    rng: BoundedRng,
    *,
    form_settings: FormTransitionSettings = FormTransitionSettings(),
) -> PostMatchPersistenceSummary:
    """Compatibility wrapper for proven generic Condition/injury/Form state.

    The autonomous Premier League path uses the more exact split sequence:
    sync_post_match_conditions -> persist_premier_league_match_incidents ->
    persist_post_match_form. This wrapper retains the earlier generic injury
    boolean behavior for isolated callers/tests that have no competition state.
    """
    runtime = tuple(runtime_participants)
    sync_post_match_conditions(side, runtime)

    side_id = int(side.side)
    injured: set[int] = set()
    for timed in result.events:
        event = timed.event
        if (
            isinstance(event, IncidentRecord)
            and event.kind is IncidentKind.INJURED
            and int(event.player_side) == side_id
        ):
            local_index = int(event.player_index)
            if not 0 <= local_index < len(runtime):
                raise IndexError(
                    f"injury player index {local_index} outside participant array"
                )
            runtime[local_index].injured = True
            injured.add(local_index)

    appeared = persist_post_match_form(
        side,
        runtime,
        result,
        rng,
        form_settings=form_settings,
    )
    return PostMatchPersistenceSummary(
        appeared_player_indices=appeared,
        injured_player_indices=frozenset(injured),
    )

@dataclass(frozen=True)
class LeagueDisciplineSummary:
    served_player_count: int
    booked_player_indices: frozenset[int]
    sent_off_player_indices: frozenset[int]
    suspended_for_next_fixture_count: int


def serve_league_suspension_after_fixture(
    player: MutableLeagueDisciplinePlayer,
    fixture_date: date,
) -> bool:
    """Exact normal-League 0x419490 general-suspension branch.

    The routine first clears the persistent suspended bit. If the general
    DBRPlayer+0x13B counter is nonzero and its +0x160 effective date is not
    later than the just-played fixture date, exactly one suspension match is
    consumed. New cards from the current match are processed only afterwards.
    """
    player.suspended = False
    remaining = int(player.suspension_matches_remaining) & 0xFF
    if remaining == 0:
        return False

    effective = player.suspension_effective_date
    if effective is not None and effective > fixture_date:
        return False

    player.suspension_matches_remaining = (remaining - 1) & 0xFF
    return True


def apply_league_match_discipline(
    player: MutableLeagueDisciplinePlayer,
    bookings: int,
    dismissals: int,
    fixture_date: date,
    rng: BoundedRng,
) -> None:
    """Exact normal-League card-to-suspension arithmetic from 0x4197C0.

    DBRPlayer fields:
      +0x139 cumulative booking counter,
      +0x13A rolling five-booking counter,
      +0x13B general suspension matches remaining,
      +0x160 suspension effective date.

    The executable processes dismissal first, then bookings. A new suspension
    created while no existing general suspension remains receives an effective
    date exactly seven days after the current match.
    """
    bookings = int(bookings) & 0xFF
    dismissals = int(dismissals) & 0xFF

    if dismissals:
        remaining = int(player.suspension_matches_remaining) & 0xFF
        if remaining == 0:
            player.suspension_effective_date = fixture_date + timedelta(days=7)

        # Exact 0x64D540(3): zero -> +3 matches, nonzero -> +1 match.
        addition = 3 if int(rng.randbelow(3)) == 0 else 1
        player.suspension_matches_remaining = (remaining + addition) & 0xFF

    if not bookings:
        return

    total = int(player.discipline_yellow_total) & 0xFF
    cycle = int(player.discipline_yellow_cycle) & 0xFF
    remaining = int(player.suspension_matches_remaining) & 0xFF

    # Exact pre-increment modulo-13 branch at 0x41991E..0x419969.
    if total % 13 == 12:
        if remaining == 0:
            player.suspension_effective_date = fixture_date + timedelta(days=7)
        remaining = (remaining + 3) & 0xFF

    total = (total + bookings) & 0xFF
    cycle = (cycle + bookings) & 0xFF

    # The original performs one threshold check/subtraction, not a loop.
    if cycle >= 5:
        cycle = (cycle - 5) & 0xFF
        if remaining == 0:
            player.suspension_effective_date = fixture_date + timedelta(days=7)
        remaining = (remaining + 1) & 0xFF

    player.discipline_yellow_total = total
    player.discipline_yellow_cycle = cycle
    player.suspension_matches_remaining = remaining


def refresh_league_suspension_for_next_fixture(
    player: MutableLeagueDisciplinePlayer,
    next_fixture_date: date | None,
) -> bool:
    """Exact normal-League 0x419680 suspended-bit refresh.

    With a known next competition fixture, the bit is set only when the general
    suspension counter is nonzero and its effective date is on/before that next
    fixture. With no fixture context the original sets the bit whenever the
    counter is nonzero.
    """
    remaining = int(player.suspension_matches_remaining) & 0xFF
    if remaining == 0:
        player.suspended = False
        return False

    if next_fixture_date is None:
        player.suspended = True
        return True

    effective = player.suspension_effective_date
    player.suspended = effective is None or effective <= next_fixture_date
    return bool(player.suspended)


def persist_premier_league_discipline(
    roster: Sequence[MutableLeagueDisciplinePlayer],
    participants: Sequence[MutableLeagueDisciplinePlayer],
    side: int,
    result: NormalMatchResult,
    fixture_date: date,
    next_fixture_date: date | None,
    rng: BoundedRng,
) -> LeagueDisciplineSummary:
    """Reproduce the normal-League post-match discipline ordering in 0x5127A0.

    Phase 1: 0x419490 over the complete team roster, serving an already-active
    suspension against the match just played.

    Phase 2: 0x4197C0 over MatchCalculator participants in participant order,
    using type-5 BOOKED/SENT_OFF records as the clean-room equivalent of the
    original participant +0x48/+0x49 counters.

    Phase 3: 0x419680 over the complete roster, setting availability for the
    next competition fixture according to the seven-day effective-date gate.
    """
    side = int(side)
    if side not in (0, 1):
        raise ValueError("side must be 0 or 1")

    served = sum(
        int(serve_league_suspension_after_fixture(player, fixture_date))
        for player in roster
    )

    bookings: dict[int, int] = {}
    dismissals: dict[int, int] = {}
    for timed in result.events:
        event = timed.event
        if not isinstance(event, IncidentRecord) or int(event.player_side) != side:
            continue
        local_index = int(event.player_index)
        if event.kind is IncidentKind.BOOKED:
            bookings[local_index] = bookings.get(local_index, 0) + 1
        elif event.kind is IncidentKind.SENT_OFF:
            dismissals[local_index] = dismissals.get(local_index, 0) + 1

    for local_index, player in enumerate(participants):
        apply_league_match_discipline(
            player,
            bookings.get(local_index, 0),
            dismissals.get(local_index, 0),
            fixture_date,
            rng,
        )

    suspended_count = sum(
        int(refresh_league_suspension_for_next_fixture(player, next_fixture_date))
        for player in roster
    )

    return LeagueDisciplineSummary(
        served_player_count=served,
        booked_player_indices=frozenset(bookings),
        sent_off_player_indices=frozenset(dismissals),
        suspended_for_next_fixture_count=suspended_count,
    )

