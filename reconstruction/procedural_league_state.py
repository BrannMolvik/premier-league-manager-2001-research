"""Live generic procedural-League state for Gate 12 Europe.

Startup already materializes every procedural LeagueMatch node and its symbolic
ClubRefs. This module begins only after those refs resolve. It accumulates the
ordinary 3/1/0 table fields and exposes a ranking only when the instruction-
backed points / goal-difference / goals-for keys uniquely determine every
position. The still-untraced final equal-key fallback is never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from competition_schedule import StartupScheduleNode
from competition_startup import CupClubRefDescriptor
from competition_state import LeagueRow


@dataclass(frozen=True)
class ProceduralLeagueFixture:
    node_token: tuple
    home_club_id: int
    away_club_id: int

    def __post_init__(self) -> None:
        if int(self.home_club_id) == int(self.away_club_id):
            raise ValueError("procedural League fixture requires two clubs")


@dataclass(frozen=True)
class ProceduralLeagueResult:
    node_token: tuple
    home_goals: int
    away_goals: int

    def __post_init__(self) -> None:
        if int(self.home_goals) < 0 or int(self.away_goals) < 0:
            raise ValueError("goals must be non-negative")


@dataclass
class LiveProceduralLeagueState:
    competition_id: int
    competition_context: int
    fixtures: dict[tuple, ProceduralLeagueFixture]
    club_ids: tuple[int, ...]
    results: dict[tuple, ProceduralLeagueResult] = field(default_factory=dict)

    @classmethod
    def from_schedule_nodes(
        cls,
        nodes: Iterable[StartupScheduleNode],
        resolve_ref: Callable[[CupClubRefDescriptor], int | None],
    ) -> "LiveProceduralLeagueState | None":
        """Materialize one competition/context only when every fixture resolves.

        European MiniLeague child fixtures can depend on earlier symbolic
        competition-position refs. Returning None preserves that pending
        boundary rather than manufacturing participant identities.
        """
        node_list = tuple(nodes)
        if not node_list:
            raise ValueError("procedural League state requires schedule nodes")

        first = node_list[0]
        competition_id = int(first.competition_id)
        competition_context = int(first.competition_context)
        fixtures: dict[tuple, ProceduralLeagueFixture] = {}
        club_order: list[int] = []

        for node in node_list:
            if str(node.node_kind) != "league_match":
                raise ValueError("procedural League state accepts league_match nodes only")
            if (
                int(node.competition_id) != competition_id
                or int(node.competition_context) != competition_context
            ):
                raise ValueError("procedural League nodes must share competition/context")

            home = resolve_ref(node.participant_0_ref)
            away = resolve_ref(node.participant_1_ref)
            if home is None or away is None:
                return None
            home = int(home)
            away = int(away)
            token = tuple(node.node_token)
            if token in fixtures:
                raise ValueError("duplicate procedural League node token")
            fixtures[token] = ProceduralLeagueFixture(token, home, away)
            if home not in club_order:
                club_order.append(home)
            if away not in club_order:
                club_order.append(away)

        return cls(
            competition_id=competition_id,
            competition_context=competition_context,
            fixtures=fixtures,
            club_ids=tuple(club_order),
        )

    def record_result(
        self,
        node_token: tuple,
        home_goals: int,
        away_goals: int,
    ) -> ProceduralLeagueResult:
        token = tuple(node_token)
        if token not in self.fixtures:
            raise KeyError(token)
        if token in self.results:
            raise ValueError("procedural League match already has a result")
        result = ProceduralLeagueResult(
            token,
            int(home_goals),
            int(away_goals),
        )
        self.results[token] = result
        return result

    def table(self) -> tuple[LeagueRow, ...]:
        rows = {club_id: LeagueRow(club_id) for club_id in self.club_ids}
        for token, result in self.results.items():
            fixture = self.fixtures[token]
            rows[fixture.home_club_id].record(
                result.home_goals,
                result.away_goals,
            )
            rows[fixture.away_club_id].record(
                result.away_goals,
                result.home_goals,
            )
        return tuple(
            sorted(
                rows.values(),
                key=lambda row: (
                    -row.points,
                    -row.goal_difference,
                    -row.goals_for,
                    row.club_id,
                ),
            )
        )

    def exact_ranking(
        self,
        club_name_key: Callable[[int], bytes | None] | None = None,
    ) -> tuple[int, ...] | None:
        """Return the exact 0x4F45E0 League ranking when names are available.

        The recovered comparator orders points descending, played ascending,
        goal difference descending, goals for descending, goals against
        ascending, then the DBRClub short-name byte string lexically. Callers
        without the source-name key remain conservative on a numeric tie.
        """
        rows = tuple(self.table())

        def numeric_key(row):
            return (
                -int(row.points),
                int(row.played),
                -int(row.goal_difference),
                -int(row.goals_for),
                int(row.goals_against),
            )

        numeric_keys = tuple(numeric_key(row) for row in rows)
        if len(numeric_keys) == len(set(numeric_keys)):
            return tuple(int(row.club_id) for row in sorted(rows, key=numeric_key))
        if club_name_key is None:
            return None
        named_rows = []
        for row in rows:
            name_key = club_name_key(int(row.club_id))
            if name_key is None:
                return None
            named_rows.append((row, bytes(name_key)))
        return tuple(
            int(row.club_id)
            for row, _name_key in sorted(
                named_rows,
                key=lambda item: numeric_key(item[0]) + (item[1],),
            )
        )

    @property
    def is_complete(self) -> bool:
        return len(self.results) == len(self.fixtures)

    def publish_exact_ranking(
        self,
        registry,
        club_name_key: Callable[[int], bytes | None] | None = None,
    ) -> tuple[int, ...] | None:
        # Competition-position ClubRefs feed later rounds/phases. Do not expose
        # a transient mid-group table merely because its currently proven sort
        # keys happen to be unique.
        ranking = self.exact_ranking(club_name_key) if self.is_complete else None
        if ranking is None:
            registry.clear_competition_ranking(
                self.competition_id,
                competition_context=self.competition_context,
            )
            return None
        return registry.replace_competition_ranking(
            self.competition_id,
            ranking,
            competition_context=self.competition_context,
        )

    def snapshot(self) -> dict:
        return {
            "competition_id": int(self.competition_id),
            "competition_context": int(self.competition_context),
            "club_ids": [int(club_id) for club_id in self.club_ids],
            "fixtures": [
                {
                    "node_token": list(fixture.node_token),
                    "home_club_id": int(fixture.home_club_id),
                    "away_club_id": int(fixture.away_club_id),
                }
                for _, fixture in sorted(
                    self.fixtures.items(),
                    key=lambda item: repr(item[0]),
                )
            ],
            "results": [
                {
                    "node_token": list(result.node_token),
                    "home_goals": int(result.home_goals),
                    "away_goals": int(result.away_goals),
                }
                for _, result in sorted(
                    self.results.items(),
                    key=lambda item: repr(item[0]),
                )
            ],
        }

    @classmethod
    def restore(cls, value: dict) -> "LiveProceduralLeagueState":
        def tup(raw):
            if isinstance(raw, list):
                return tuple(tup(item) for item in raw)
            return raw

        fixtures = {}
        for raw in value.get("fixtures", ()):
            token = tup(raw["node_token"])
            fixtures[token] = ProceduralLeagueFixture(
                token,
                int(raw["home_club_id"]),
                int(raw["away_club_id"]),
            )
        state = cls(
            competition_id=int(value["competition_id"]),
            competition_context=int(value.get("competition_context", 0)),
            fixtures=fixtures,
            club_ids=tuple(int(v) for v in value.get("club_ids", ())),
        )
        for raw in value.get("results", ()):
            state.record_result(
                tup(raw["node_token"]),
                int(raw["home_goals"]),
                int(raw["away_goals"]),
            )
        return state
