"""Read-only source-data bridge for future original FM2001 management screens.

Gate 13 must keep presentation separate from simulation while preserving the
original game's recovered data/order semantics. This module exposes immutable
view data from the existing HumanGameplayController/GameState boundary only.

It deliberately DOES NOT define original screen IDs, widgets, coordinates,
fonts, colors, navigation, fixture-screen sorting, or other visual semantics
that have not yet been recovered from the authorized original executable/art.
Fixture rows preserve DBRRealFixture/runtime source insertion order; table rows
preserve GameState.premier_league_table(), which uses the recovered native
League comparator whenever original CP1252 short names are available.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class ManagementPresentationError(ValueError):
    pass


@dataclass(frozen=True)
class ClubHeaderView:
    club_id: int
    name: str
    short_name: str
    current_date: date


@dataclass(frozen=True)
class SquadRowView:
    source_roster_index: int
    player_id: int
    full_name: str
    shirt_number: int
    positions: tuple[int, int, int]
    condition: int
    form_state: int
    morale: int
    injured: bool
    suspended: bool
    out_of_contract: bool
    transfer_listed: bool
    loan_listed: bool
    wanted: bool


@dataclass(frozen=True)
class FixtureRowView:
    source_fixture_index: int
    fixture_id: int
    round_index: int
    scheduled_date: date | None
    home_club_id: int
    home_club_name: str
    away_club_id: int
    away_club_name: str
    played: bool
    home_goals: int | None
    away_goals: int | None


@dataclass(frozen=True)
class LeagueTableRowView:
    position: int
    club_id: int
    club_name: str
    short_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


@dataclass(frozen=True)
class TacticsSelectionView:
    formation_id: int
    starter_ids: tuple[int, ...]
    substitute_ids: tuple[int, ...]
    play_style: int
    without_ball_style: int
    with_ball_style: int
    aggression: int
    captain_priority: tuple[int, ...]
    penalty_priority: tuple[int, ...]
    corner_priority: tuple[int, ...]
    free_kick_priority: tuple[int, ...]


@dataclass(frozen=True)
class PlayerProfileView:
    player_id: int
    first_name: str
    surname: str
    club_id: int
    club_name: str
    nationality_id: int
    date_of_birth: date | None
    shirt_number: int
    height_cm: int
    weight_kg: int
    positions: tuple[int, int, int]
    current_skill_bytes: tuple[int, ...]
    condition: int
    form_state: int
    morale: int
    weekly_wage: int
    contract_expiry_date: date | None
    injured: bool
    suspended: bool
    out_of_contract: bool
    transfer_listed: bool
    loan_listed: bool
    wanted: bool
    loan_club_id: int | None


@dataclass(frozen=True)
class ManagementSourceDataSnapshot:
    club: ClubHeaderView
    squad: tuple[SquadRowView, ...]
    tactics: TacticsSelectionView
    fixtures_in_source_order: tuple[FixtureRowView, ...]
    league_table: tuple[LeagueTableRowView, ...]


class ManagementSourceDataBridge:
    """Project recovered backend state into immutable presentation data.

    The bridge never advances time, mutates a lineup, performs a transfer, or
    simulates a match. The future original-resource renderer may consume these
    rows after its native control/layout behavior is independently recovered.
    """

    def __init__(self, controller):
        self.controller = controller

    @property
    def state(self):
        state = getattr(self.controller, "state", None)
        if state is None:
            raise ManagementPresentationError(
                "Management presentation requires a live game state"
            )
        return state

    def _human_club_id(self) -> int:
        human = getattr(self.controller, "human", None)
        if human is None:
            raise ManagementPresentationError(
                "Select a human-managed club before opening management presentation"
            )
        club_id = getattr(human, "club_id", None)
        if type(club_id) is not int:
            raise ManagementPresentationError("Human club ID is unavailable")
        return club_id

    def _source_club(self, club_id: int):
        clubs = getattr(self.state, "clubs", None)
        if not hasattr(clubs, "get"):
            raise ManagementPresentationError("Source club table is unavailable")
        club = clubs.get(int(club_id))
        if club is None:
            raise ManagementPresentationError(f"Unknown source club {club_id}")
        if not isinstance(getattr(club, "name", None), str):
            raise ManagementPresentationError(
                f"Source club {club_id} has no recovered display name"
            )
        if not isinstance(getattr(club, "short_name", None), str):
            raise ManagementPresentationError(
                f"Source club {club_id} has no recovered short name"
            )
        return club

    @staticmethod
    def _player_name(player) -> str:
        first = getattr(player, "first_name", None)
        surname = getattr(player, "surname", None)
        if not isinstance(first, str) or not isinstance(surname, str):
            raise ManagementPresentationError(
                "Runtime player lacks recovered source name fields"
            )
        return f"{first} {surname}".strip()

    def club_header(self) -> ClubHeaderView:
        club_id = self._human_club_id()
        club = self._source_club(club_id)
        calendar = getattr(self.state, "calendar", None)
        current_date = getattr(calendar, "current_date", None)
        if not isinstance(current_date, date):
            raise ManagementPresentationError("Game calendar date is unavailable")
        return ClubHeaderView(
            club_id=club_id,
            name=club.name,
            short_name=club.short_name,
            current_date=current_date,
        )

    def squad_rows(self) -> tuple[SquadRowView, ...]:
        self._human_club_id()
        squad = getattr(self.controller, "squad", None)
        if not callable(squad):
            raise ManagementPresentationError("Controlled-club roster is unavailable")
        rows = []
        for source_index, player in enumerate(tuple(squad())):
            player_id = getattr(player, "index", None)
            positions = getattr(player, "positions", None)
            if type(player_id) is not int:
                raise ManagementPresentationError("Runtime player ID is unavailable")
            if (
                not isinstance(positions, tuple)
                or len(positions) != 3
                or any(type(value) is not int for value in positions)
            ):
                raise ManagementPresentationError(
                    f"Player {player_id} has no recovered three-position tuple"
                )
            rows.append(SquadRowView(
                source_roster_index=source_index,
                player_id=player_id,
                full_name=self._player_name(player),
                shirt_number=int(getattr(player, "shirt_number", 0)),
                positions=positions,
                condition=int(getattr(player, "condition")),
                form_state=int(getattr(player, "form_state")),
                morale=int(getattr(player, "morale")),
                injured=bool(getattr(player, "injured")),
                suspended=bool(getattr(player, "suspended")),
                out_of_contract=bool(getattr(player, "out_of_contract")),
                transfer_listed=bool(getattr(player, "transfer_listed")),
                loan_listed=bool(getattr(player, "loan_listed")),
                wanted=bool(getattr(player, "wanted")),
            ))
        return tuple(rows)

    def tactics_selection(self) -> TacticsSelectionView:
        """Expose exact backend tactical/selection state without UI labels.

        TeamTacticalState's four values are recovered runtime fields and
        TeamOrderPriorities maps the four original stored priority lists.
        Formation/player IDs are the currently persisted human selection.
        """
        club_id = self._human_club_id()
        human = self.controller.human
        team_tactics = getattr(self.state, "team_tactics", None)
        if not hasattr(team_tactics, "get"):
            raise ManagementPresentationError(
                "Recovered team tactical state is unavailable"
            )
        tactics = team_tactics.get(club_id)
        if tactics is None:
            raise ManagementPresentationError(
                f"Controlled club {club_id} has no recovered tactical state"
            )
        orders = getattr(human, "team_orders", None)
        required_order_fields = ("captain", "penalty", "corner", "free_kick")
        if orders is None or any(
            not isinstance(getattr(orders, name, None), tuple)
            for name in required_order_fields
        ):
            raise ManagementPresentationError(
                "Recovered human Team Orders priority lists are unavailable"
            )
        starter_ids = getattr(human, "starter_ids", None)
        substitute_ids = getattr(human, "substitute_ids", None)
        if not isinstance(starter_ids, tuple) or not isinstance(substitute_ids, tuple):
            raise ManagementPresentationError(
                "Recovered human lineup selection is unavailable"
            )
        if any(type(value) is not int for value in starter_ids + substitute_ids):
            raise ManagementPresentationError(
                "Human lineup player IDs must remain integer source IDs"
            )
        formation_id = getattr(human, "formation_id", None)
        if type(formation_id) is not int:
            raise ManagementPresentationError("Human formation ID is unavailable")
        return TacticsSelectionView(
            formation_id=formation_id,
            starter_ids=starter_ids,
            substitute_ids=substitute_ids,
            play_style=int(getattr(tactics, "play_style")),
            without_ball_style=int(getattr(tactics, "without_ball_style")),
            with_ball_style=int(getattr(tactics, "with_ball_style")),
            aggression=int(getattr(tactics, "aggression")),
            captain_priority=tuple(int(v) for v in orders.captain),
            penalty_priority=tuple(int(v) for v in orders.penalty),
            corner_priority=tuple(int(v) for v in orders.corner),
            free_kick_priority=tuple(int(v) for v in orders.free_kick),
        )

    def player_profile(self, player_id: int) -> PlayerProfileView:
        """Expose recovered runtime/source player data without invented UI labels.

        The current 17-byte skill vector is the live DBRPlayer state already
        reconstructed by the backend. Development target bytes are deliberately
        NOT exposed here because they are not established as player-profile UI.
        """
        if type(player_id) is not int:
            raise ManagementPresentationError("Player profile ID must be an integer")
        players = getattr(self.state, "players", None)
        if not hasattr(players, "get"):
            raise ManagementPresentationError("Runtime player table is unavailable")
        player = players.get(player_id)
        if player is None:
            raise ManagementPresentationError(f"Unknown runtime player {player_id}")
        first = getattr(player, "first_name", None)
        surname = getattr(player, "surname", None)
        if not isinstance(first, str) or not isinstance(surname, str):
            raise ManagementPresentationError(
                f"Player {player_id} lacks recovered source name fields"
            )
        club_id = getattr(player, "club_id", None)
        nationality_id = getattr(player, "nationality_id", None)
        if type(club_id) is not int or type(nationality_id) is not int:
            raise ManagementPresentationError(
                f"Player {player_id} lacks recovered club/nationality IDs"
            )
        club = self._source_club(club_id)
        positions = getattr(player, "positions", None)
        if (
            not isinstance(positions, tuple)
            or len(positions) != 3
            or any(type(value) is not int for value in positions)
        ):
            raise ManagementPresentationError(
                f"Player {player_id} has no recovered three-position tuple"
            )
        current = getattr(player, "current_raw", None)
        if (
            not isinstance(current, (list, tuple))
            or len(current) != 17
            or any(type(value) is not int for value in current)
        ):
            raise ManagementPresentationError(
                f"Player {player_id} has no recovered 17-byte current-skill vector"
            )
        dob = getattr(player, "date_of_birth", None)
        if dob is not None and not isinstance(dob, date):
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered date of birth"
            )
        expiry = getattr(player, "contract_expiry_date", None)
        if expiry is not None and not isinstance(expiry, date):
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered contract expiry"
            )
        loan_club = getattr(player, "loan_club_id", None)
        if loan_club is not None and type(loan_club) is not int:
            raise ManagementPresentationError(
                f"Player {player_id} has invalid recovered loan club ID"
            )
        return PlayerProfileView(
            player_id=player_id,
            first_name=first,
            surname=surname,
            club_id=club_id,
            club_name=club.name,
            nationality_id=nationality_id,
            date_of_birth=dob,
            shirt_number=int(getattr(player, "shirt_number")),
            height_cm=int(getattr(player, "height_cm")),
            weight_kg=int(getattr(player, "weight_kg")),
            positions=positions,
            current_skill_bytes=tuple(current),
            condition=int(getattr(player, "condition")),
            form_state=int(getattr(player, "form_state")),
            morale=int(getattr(player, "morale")),
            weekly_wage=int(getattr(player, "weekly_wage")),
            contract_expiry_date=expiry,
            injured=bool(getattr(player, "injured")),
            suspended=bool(getattr(player, "suspended")),
            out_of_contract=bool(getattr(player, "out_of_contract")),
            transfer_listed=bool(getattr(player, "transfer_listed")),
            loan_listed=bool(getattr(player, "loan_listed")),
            wanted=bool(getattr(player, "wanted")),
            loan_club_id=loan_club,
        )

    def fixture_rows(self) -> tuple[FixtureRowView, ...]:
        league = getattr(self.state, "premier_league", None)
        if league is None:
            raise ManagementPresentationError("Premier League state is unavailable")
        source_order = getattr(league, "fixture_source_order", None)
        fixtures = getattr(league, "fixtures", None)
        results = getattr(league, "results", None)
        round_date = getattr(league, "round_date", None)
        if (
            not isinstance(source_order, tuple)
            or not hasattr(fixtures, "get")
            or not hasattr(results, "get")
            or not callable(round_date)
        ):
            raise ManagementPresentationError(
                "Recovered Premier League fixture source ordering is unavailable"
            )
        rows = []
        for source_index, fixture_id in enumerate(source_order):
            fixture = fixtures.get(int(fixture_id))
            if fixture is None:
                raise ManagementPresentationError(
                    f"Source-order fixture {fixture_id} is missing"
                )
            home_id = int(fixture.home_club_id)
            away_id = int(fixture.away_club_id)
            home = self._source_club(home_id)
            away = self._source_club(away_id)
            result = results.get(int(fixture_id))
            scheduled = round_date(int(fixture.round_index))
            if scheduled is not None and not isinstance(scheduled, date):
                raise ManagementPresentationError(
                    f"Fixture {fixture_id} has invalid recovered date"
                )
            rows.append(FixtureRowView(
                source_fixture_index=source_index,
                fixture_id=int(fixture_id),
                round_index=int(fixture.round_index),
                scheduled_date=scheduled,
                home_club_id=home_id,
                home_club_name=home.name,
                away_club_id=away_id,
                away_club_name=away.name,
                played=result is not None,
                home_goals=(None if result is None else int(result.home_goals)),
                away_goals=(None if result is None else int(result.away_goals)),
            ))
        return tuple(rows)

    def league_table_rows(self) -> tuple[LeagueTableRowView, ...]:
        table = getattr(self.state, "premier_league_table", None)
        if not callable(table):
            raise ManagementPresentationError(
                "Recovered Premier League table projection is unavailable"
            )
        rows = []
        for position, row in enumerate(tuple(table()), start=1):
            club_id = int(row.club_id)
            club = self._source_club(club_id)
            rows.append(LeagueTableRowView(
                position=position,
                club_id=club_id,
                club_name=club.name,
                short_name=club.short_name,
                played=int(row.played),
                wins=int(row.wins),
                draws=int(row.draws),
                losses=int(row.losses),
                goals_for=int(row.goals_for),
                goals_against=int(row.goals_against),
                goal_difference=int(row.goal_difference),
                points=int(row.points),
            ))
        return tuple(rows)

    def snapshot(self) -> ManagementSourceDataSnapshot:
        return ManagementSourceDataSnapshot(
            club=self.club_header(),
            squad=self.squad_rows(),
            tactics=self.tactics_selection(),
            fixtures_in_source_order=self.fixture_rows(),
            league_table=self.league_table_rows(),
        )
