from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol, Sequence

from match_role_rating import best_preferred_role_rating


class FormationSelectionClass(IntEnum):
    """Exact 0x409500 output classes consumed by 0x409B50."""

    NO_CONTEXT = 0
    ATTACKING = 1
    NORMAL = 2
    DEFENSIVE = 3


# Defaults stored in the analyzed executable and optionally tuning-overridable.
GS_DEF_PERC = -3
GS_ATT_PERC = 3
GS_HOME_VALUE = 1
GS_AWAY_VALUE = -1
GS_RATING_DIV = 10000
GS_CUP_FINAL_BIAS = 3
GS_CUP_SEMI_FINAL_BIAS = 2
GS_CUP_QUARTER_FINAL_BIAS = 1
GS_PRECEDENCE_DIV = 3
GS_GO_FOR_WIN_LEAGUE_BIAS = 2
GS_GO_FOR_PROMOTION_BIAS = 1
GS_GO_FOR_AVOID_RELEGATION_BIAS = 1
GS_GO_FOR_AVOID_RELEGATION_PLAYOFF_BIAS = 3
GS_START_WORRYING_ABOUT_LEAGUE_POS = 8
GS_REALLY_WORRYING_ABOUT_LEAGUE_POS = 4


def formation_selection_class_from_score(
    score: int,
    *,
    defensive_threshold: int = GS_DEF_PERC,
    attacking_threshold: int = GS_ATT_PERC,
) -> FormationSelectionClass:
    """Exact final bucketing at 0x40964A..0x409678.

    The original tuning keys are GSDefPerc and GSAttPerc. Scores at or below
    the defensive threshold use manager formation byte +0x21; scores at or
    above the attacking threshold use +0x22; values between use the default
    formation. NO_CONTEXT is returned elsewhere by 0x409500 before bucketing.
    """
    value = int(score)
    if value <= int(defensive_threshold):
        return FormationSelectionClass.DEFENSIVE
    if value < int(attacking_threshold):
        return FormationSelectionClass.NORMAL
    return FormationSelectionClass.ATTACKING


def rating_difference_pressure(
    current_rating: int,
    opponent_rating: int,
    *,
    divisor: int = GS_RATING_DIV,
) -> int:
    """Exact relative-squad-rating contribution inside 0x409500.

    0x409900 sums 0x41E1D0 over at most the first eleven team-roster entries.
    The signed difference is divided with C/IA-32 truncation toward zero and
    converted to a 0..5 pressure step at absolute thresholds 5/10/20/50/100.
    A stronger current team subtracts the step; a weaker team adds it.
    """
    divisor = int(divisor)
    if divisor == 0:
        raise ValueError("rating divisor must be non-zero")

    delta = int((int(current_rating) - int(opponent_rating)) / divisor)
    magnitude = abs(delta)
    if magnitude >= 100:
        step = 5
    elif magnitude >= 50:
        step = 4
    elif magnitude >= 20:
        step = 3
    elif magnitude >= 10:
        step = 2
    elif magnitude >= 5:
        step = 1
    else:
        step = 0

    if delta > 0:
        return -step
    return step


def aggregate_deficit_pressure(goals_behind: int) -> int:
    """Exact positive aggregate/score deficit boost in the type-2 branch.

    0x409500 adds no score pressure while level/ahead, then adds:
    1 behind -> 2, 2 behind -> 5, 3 behind -> 6, 4+ behind -> 7.
    """
    deficit = int(goals_behind)
    if deficit >= 4:
        return 7
    if deficit == 3:
        return 6
    if deficit == 2:
        return 5
    if deficit == 1:
        return 2
    return 0


def cup_round_strategy_bias(
    rounds_from_final: int,
    competition_precedence: int,
    *,
    final_bias: int = GS_CUP_FINAL_BIAS,
    semi_final_bias: int = GS_CUP_SEMI_FINAL_BIAS,
    quarter_final_bias: int = GS_CUP_QUARTER_FINAL_BIAS,
    precedence_divisor: int = GS_PRECEDENCE_DIV,
) -> int:
    """Exact cup-path contribution returned by 0x409680.

    rounds_from_final is the difference used by the executable before its
    1/2/3 mapping: 1 final, 2 semi-final, 3 quarter-final.
    """
    rounds_from_final = int(rounds_from_final)
    if rounds_from_final == 1:
        base = int(final_bias)
    elif rounds_from_final == 2:
        base = int(semi_final_bias)
    elif rounds_from_final == 3:
        base = int(quarter_final_bias)
    else:
        base = 0

    precedence_divisor = int(precedence_divisor)
    if precedence_divisor == 0:
        raise ValueError("precedence divisor must be non-zero")
    return base + int((int(competition_precedence) + 12) / precedence_divisor)


def league_objective_pressure(
    points_gap: int,
    matches_remaining: int,
    base_bias: int,
    *,
    start_worrying: int = GS_START_WORRYING_ABOUT_LEAGUE_POS,
    really_worrying: int = GS_REALLY_WORRYING_ABOUT_LEAGUE_POS,
) -> int:
    """Exact per-objective late-season pressure arithmetic from 0x409680.

    The surrounding competition helper decides which one of five objectives
    (win league, promotion, promotion playoff, avoid relegation, relegation
    playoff) is currently applicable. This function reconstructs the common
    arithmetic once that objective gap is known.
    """
    remaining = int(matches_remaining)
    gap = int(points_gap)
    if remaining <= 0 or remaining > int(start_worrying) or gap <= 0:
        return 0

    required_per_match = gap / remaining
    if required_per_match >= 3.0:
        return 0

    # Executable uses x87 value + 0.499 followed by truncation.
    pressure = int(required_per_match + 0.499) + int(base_bias)
    if remaining > int(really_worrying):
        # Exact signed divide-by-two sequence, truncating toward zero.
        pressure = int(pressure / 2)
    return pressure



@dataclass(frozen=True)
class LeagueObjectiveGaps:
    """Five ordered point-gap outputs produced by 0x4F8C50."""

    win_league: int | None = None
    promotion: int | None = None
    promotion_playoff: int | None = None
    avoid_relegation: int | None = None
    avoid_relegation_playoff: int | None = None


def league_objective_gaps_from_sorted_points(
    points_by_rank: tuple[int, ...] | list[int],
    current_rank: int,
    *,
    automatic_promotion_places: int = 0,
    playoff_places: int = 0,
    relegation_places: int = 0,
) -> LeagueObjectiveGaps:
    """Reconstruct the cut-line point gaps written by 0x4F8C50.

    points_by_rank must already be in competition table order. The original
    helper reads points as 3*wins + draws from that sorted table.
    """
    points = tuple(int(value) for value in points_by_rank)
    rank = int(current_rank)
    if not points:
        raise ValueError("points_by_rank cannot be empty")
    if not 0 <= rank < len(points):
        raise ValueError("current_rank is outside the table")
    if min(
        int(automatic_promotion_places),
        int(playoff_places),
        int(relegation_places),
    ) < 0:
        raise ValueError("place counts must be non-negative")

    auto = int(automatic_promotion_places)
    playoff = int(playoff_places)
    relegation = int(relegation_places)
    count = len(points)
    current_points = points[rank]

    if auto > count or auto + playoff > count or relegation + playoff >= count:
        raise ValueError("competition cut-line counts exceed table size")

    win_league = None
    promotion = None
    if auto:
        promotion = points[auto - 1] - current_points
    else:
        win_league = points[0] - current_points

    promotion_playoff = (
        points[auto + playoff - 1] - current_points
        if playoff
        else None
    )
    avoid_relegation = (
        points[count - relegation - 1] - current_points
        if relegation
        else None
    )
    avoid_relegation_playoff = (
        points[count - relegation - playoff - 1] - current_points
        if playoff
        else None
    )

    return LeagueObjectiveGaps(
        win_league=win_league,
        promotion=promotion,
        promotion_playoff=promotion_playoff,
        avoid_relegation=avoid_relegation,
        avoid_relegation_playoff=avoid_relegation_playoff,
    )


def _league_objective_pressure_or_none(
    points_gap: int | None,
    matches_remaining: int,
    base_bias: int | None,
) -> int | None:
    if points_gap is None:
        return None
    remaining = int(matches_remaining)
    gap = int(points_gap)
    if remaining <= 0 or remaining > GS_START_WORRYING_ABOUT_LEAGUE_POS or gap <= 0:
        return None
    required_per_match = gap / remaining
    if required_per_match >= 3.0:
        return None
    if base_bias is None:
        raise ValueError("applicable objective requires a known base bias")
    value = int(required_per_match + 0.499) + int(base_bias)
    if remaining > GS_REALLY_WORRYING_ABOUT_LEAGUE_POS:
        value = int(value / 2)
    return value


def late_season_league_strategy_bias(
    gaps: LeagueObjectiveGaps,
    matches_remaining: int,
    *,
    win_league_bias: int = GS_GO_FOR_WIN_LEAGUE_BIAS,
    promotion_bias: int = GS_GO_FOR_PROMOTION_BIAS,
    promotion_playoff_bias: int | None = None,
    avoid_relegation_bias: int = GS_GO_FOR_AVOID_RELEGATION_BIAS,
    avoid_relegation_playoff_bias: int = GS_GO_FOR_AVOID_RELEGATION_PLAYOFF_BIAS,
) -> int:
    """Exact first-applicable objective ordering used by 0x409680."""
    objectives = (
        (gaps.win_league, win_league_bias),
        (gaps.promotion, promotion_bias),
        (gaps.promotion_playoff, promotion_playoff_bias),
        (gaps.avoid_relegation, avoid_relegation_bias),
        (gaps.avoid_relegation_playoff, avoid_relegation_playoff_bias),
    )
    for gap, bias in objectives:
        value = _league_objective_pressure_or_none(
            gap,
            matches_remaining,
            bias,
        )
        if value is not None:
            return value
    return 0


def game_strategy_score(
    *,
    is_home: bool,
    current_rating: int,
    opponent_rating: int,
    aggregate_goals_behind: int = 0,
    competition_context_bias: int = 0,
) -> int:
    """Compose the additive 0x409500 strategy-score components."""
    score = GS_HOME_VALUE if bool(is_home) else GS_AWAY_VALUE
    score += rating_difference_pressure(current_rating, opponent_rating)
    score += aggregate_deficit_pressure(aggregate_goals_behind)
    score += int(competition_context_bias)
    return score


def manager_formation_for_game_strategy(
    preferences,
    *,
    is_home: bool,
    current_rating: int,
    opponent_rating: int,
    aggregate_goals_behind: int = 0,
    competition_context_bias: int = 0,
) -> int:
    """Choose the manager formation from a reconstructed 0x409500 score."""
    score = game_strategy_score(
        is_home=is_home,
        current_rating=current_rating,
        opponent_rating=opponent_rating,
        aggregate_goals_behind=aggregate_goals_behind,
        competition_context_bias=competition_context_bias,
    )
    return manager_formation_for_selection_class(
        preferences,
        formation_selection_class_from_score(score),
    )


class StrategyRatingPlayer(Protocol):
    skills: Sequence[int]
    preferred_positions: Sequence[int]


class LeagueStrategyRow(Protocol):
    club_id: int
    played: int
    points: int


def strategy_team_rating(players: Sequence[StrategyRatingPlayer]) -> int:
    """Exact 0x409900 team-rating sum used by the formation classifier.

    The executable consumes at most the first eleven entries in team roster
    order and sums 0x41E1D0, the best preferred-position role rating.
    """
    return sum(
        best_preferred_role_rating(player.skills, player.preferred_positions)
        for player in players[:11]
    )


def premier_league_strategy_bias(
    table_rows: Sequence[LeagueStrategyRow],
    club_id: int,
    *,
    total_matches: int = 38,
) -> int:
    """Reconstruct the 0x409680 league-position bias for the Premier League.

    The shipped top division has no promotion/playoff cut and three relegation
    places, so only title and avoid-relegation objectives can become active.
    """
    rows = tuple(table_rows)
    target = int(club_id)
    rank = next(
        (index for index, row in enumerate(rows) if int(row.club_id) == target),
        None,
    )
    if rank is None:
        raise KeyError(f"club {target} is not present in the league table")

    row = rows[rank]
    matches_remaining = int(total_matches) - int(row.played)
    gaps = league_objective_gaps_from_sorted_points(
        [int(item.points) for item in rows],
        rank,
        automatic_promotion_places=0,
        playoff_places=0,
        relegation_places=3,
    )
    return late_season_league_strategy_bias(gaps, matches_remaining)

class ManagerFormationSource(Protocol):
    formation_default: int
    formation_class3: int
    formation_class1: int


@dataclass(frozen=True)
class ManagerFormationPreferences:
    """Three persisted manager formation IDs consumed by 0x409B50."""

    default: int
    class3: int
    class1: int

    @classmethod
    def from_manager(cls, manager: ManagerFormationSource) -> "ManagerFormationPreferences":
        return cls(
            int(manager.formation_default),
            int(manager.formation_class3),
            int(manager.formation_class1),
        )

    def __post_init__(self) -> None:
        if not 0 <= int(self.default) <= 20:
            raise ValueError("default formation must be in 0..20")
        if not (0 <= int(self.class3) <= 20 or int(self.class3) == 0xFF):
            raise ValueError("class3 formation must be in 0..20 or 0xFF")
        if not 0 <= int(self.class1) <= 20:
            raise ValueError("class1 formation must be in 0..20")


def manager_formation_for_selection_class(
    preferences: ManagerFormationPreferences | ManagerFormationSource,
    selection_class: int,
) -> int:
    """Exact 0x409B50 mapping from 0x409500 class to manager formation byte.

    Numeric class names are intentionally preserved until the remaining
    0x409500 match-context branches are fully assigned football semantics.
    """
    if not isinstance(preferences, ManagerFormationPreferences):
        preferences = ManagerFormationPreferences.from_manager(preferences)

    selection_class = int(selection_class)
    if selection_class == int(FormationSelectionClass.NO_CONTEXT) or selection_class == int(FormationSelectionClass.NORMAL):
        formation = preferences.default
    elif selection_class == int(FormationSelectionClass.ATTACKING):
        formation = preferences.class1
    elif selection_class == int(FormationSelectionClass.DEFENSIVE):
        formation = preferences.class3
    else:
        raise ValueError("selection_class must be in 0..3")

    if formation == 0xFF:
        raise ValueError(
            "selected manager alternate formation is 0xFF; original fallback "
            "behavior must be traced before substituting another formation"
        )
    return formation


DEFAULT_SUBSTITUTE_QUOTA = 5


def resolved_substitute_quota(context_quota: int | None) -> int:
    """0x408500 fallback behavior after current-match/context resolution."""
    if context_quota is None:
        return DEFAULT_SUBSTITUTE_QUOTA
    quota = int(context_quota)
    if quota < 0:
        raise ValueError("substitute quota must be non-negative")
    return quota
class ManagerTacticalSource(Protocol):
    ai_play_style_source: int
    ai_aggression_source: int
    ai_with_ball_source: int
    ai_without_ball_source: int


@dataclass(frozen=True)
class ManagerTacticalSources:
    """Persisted DBRManager +0x30..+0x33 inputs consumed by 0x40D860.

    These are deliberately source values rather than final MatchCalculator
    tactic codes. The pre-match packet applies the exact transforms below
    before the TacticsCommand visitor consumes them.
    """

    play_style_source: int
    aggression_source: int
    with_ball_source: int
    without_ball_source: int

    @classmethod
    def from_manager(cls, manager: ManagerTacticalSource) -> "ManagerTacticalSources":
        return cls(
            int(manager.ai_play_style_source),
            int(manager.ai_aggression_source),
            int(manager.ai_with_ball_source),
            int(manager.ai_without_ball_source),
        )

    def __post_init__(self) -> None:
        for name in (
            "play_style_source",
            "aggression_source",
            "with_ball_source",
            "without_ball_source",
        ):
            value = int(getattr(self, name))
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be in 0..255")


@dataclass(frozen=True)
class TacticsPacketFields:
    """Four compact values written into the 0x40D860 pre-match packet."""

    strategy_code: int
    aggression_code: int
    with_ball_code: int
    without_ball_code: int


def play_style_to_strategy_code(play_style: int) -> int:
    """Exact switch in 0x4035E0.

    The helper is used both for live team Play style and the AI manager's
    persisted source byte. Unknown values take the executable's Normal fallback.
    """
    value = int(play_style)
    if value == 0:
        return 3
    if value == 1:
        return 2
    if value == 2:
        return 1
    return 2


def manager_tactics_packet_fields(
    sources: ManagerTacticalSources | ManagerTacticalSource,
) -> TacticsPacketFields:
    """Exact AI-side bit-field inputs built by 0x40D860.

    Do not reinterpret the returned codes as final team +0x1B4..+0x1B7 values
    until the concrete TacticsCommand visitor has been mapped.
    """
    if not isinstance(sources, ManagerTacticalSources):
        sources = ManagerTacticalSources.from_manager(sources)

    return TacticsPacketFields(
        strategy_code=play_style_to_strategy_code(sources.play_style_source),
        aggression_code=(int(sources.aggression_source) // 6) & 0x0F,
        with_ball_code=int(sources.with_ball_source) & 0x03,
        without_ball_code=int(sources.without_ball_source) & 0x03,
    )


@dataclass(frozen=True)
class TeamTacticalState:
    """Exact normal team tactical defaults from the team constructor.

    Runtime team fields:
    +0x1B4 Play style, +0x1B5 Without Ball, +0x1B6 With Ball,
    +0x1B7 Aggression.
    """

    play_style: int = 1
    without_ball_style: int = 0
    with_ball_style: int = 0
    aggression: int = 5

    def __post_init__(self) -> None:
        if not 0 <= int(self.play_style) <= 2:
            raise ValueError("play_style must be in 0..2")
        if not 0 <= int(self.without_ball_style) <= 3:
            raise ValueError("without_ball_style must be in 0..3")
        if not 0 <= int(self.with_ball_style) <= 3:
            raise ValueError("with_ball_style must be in 0..3")
        if not 0 <= int(self.aggression) <= 9:
            raise ValueError("aggression must be in 0..9")


def team_tactics_packet_fields(state: TeamTacticalState) -> TacticsPacketFields:
    """Exact user-controlled 0x40D860 packet packing inputs."""
    return TacticsPacketFields(
        strategy_code=play_style_to_strategy_code(state.play_style),
        aggression_code=int(state.aggression) & 0x0F,
        with_ball_code=int(state.with_ball_style) & 0x03,
        without_ball_code=int(state.without_ball_style) & 0x03,
    )
