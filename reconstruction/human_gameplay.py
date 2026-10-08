"""Minimum human-manager gameplay controller for Gate 7.

This is intentionally a backend workflow layer, not a replacement UI. It keeps
one human club's persistent selection/tactics while every match still runs
through GameState's reconstructed Premier League simulation backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from time import time
from typing import Callable, Iterable

from game_state import GameState
from original_management_advance import (
    NATIVE_DEFAULT_TURN_LENGTH,
    OriginalManagementAdvanceTarget,
    original_management_advance_target,
)
from match_engine_rng import MatchEngineRng
from match_lineup import AI_FORMATIONS, AiLineupCoreResult, StarterAssignment
from match_orders import TeamOrderPriorities
from match_participants import collect_match_participants
from match_preparation import PreparedAiMatchSelection, prepare_ai_match_selection
from match_schedule import MsvcCrtRng
from match_team_setup import TeamTacticalState, resolved_substitute_quota
from scouting import (
    SCOUTING_SORT_MODE_CLUB_NAME,
    SCOUTING_SORT_MODE_HISTORY_AVERAGE,
    SCOUTING_SORT_MODE_POSITION_LABEL,
    SCOUTING_SORT_MODE_VALUE,
    ScoutingFilterControls,
    ScoutingFilterValues,
    ScoutingRankValues,
    ScoutingReseedState,
    ScoutingSortValues,
    run_scouting_search,
    scouting_country_context_passes,
    scouting_first_stage_passes,
    scouting_loan_list_user_match,
    scouting_preferred_position_passes,
    scouting_strength_threshold_passes,
)
from transfer_decision import SellingClubDecision
from transfer_negotiation import (
    OrdinaryMoneyResponse,
    OrdinaryMoneyResponseResult,
    evaluate_ordinary_money_response,
)
from transfer_state import ContractTerms
from transfer_workflow import (
    LiveCashBidEvaluation,
    evaluate_live_cash_bid,
    execute_due_ordinary_cash_transfers,
    schedule_ordinary_cash_transfer,
    submit_live_cash_bid,
)


def _annual_cup_child_procedural_ids(
    competitions: Iterable[object],
    cup_source_ids: Iterable[int],
) -> tuple[int, ...]:
    """Return procedural League children required by annual Cup sources."""
    cup_sources = {int(value) for value in cup_source_ids}
    return tuple(
        int(competition.id)
        for competition in competitions
        if int(getattr(competition, "runtime_kind_code", 0)) == 1
        and getattr(competition, "parent_competition_id", None) is not None
        and int(competition.parent_competition_id) in cup_sources
    )


@dataclass
class HumanManagerState:
    club_id: int
    formation_id: int = 0
    starter_ids: tuple[int, ...] = ()
    substitute_ids: tuple[int, ...] = ()
    team_orders: TeamOrderPriorities = field(default_factory=TeamOrderPriorities)


@dataclass(frozen=True)
class HumanPrimaryMatchdayOutcome:
    match_entry: tuple
    user_result: object
    matchday_results: tuple[tuple[tuple, object], ...]
    table: tuple[object, ...]


@dataclass(frozen=True)
class HumanMatchdayOutcome:
    fixture_id: int
    user_result: object
    matchday_results: tuple[tuple[int, object], ...]
    table: tuple[object, ...]


@dataclass(frozen=True)
class OriginalManagementTurnOutcome:
    """Bounded NEXT day walk; a pending entry still needs native modal choice."""

    target: OriginalManagementAdvanceTarget
    processed_dates: tuple[date, ...]
    pending_primary_entry: tuple | None


class HumanGameplayController:
    """Small persistent gameplay loop over the reconstructed match backend."""

    def __init__(
        self,
        state: GameState,
        attack_matrix,
        defence_matrix,
        match_rng,
        match_engine_rng=None,
        *,
        playable_primary_procedural_ids: Iterable[int] = (),
        playable_primary_club_ids: Iterable[int] = (),
        playable_country_allocation_plan=None,
    ):
        if state.premier_league is None:
            raise RuntimeError("Premier League state is required")
        self.state = state
        self.attack_matrix = attack_matrix
        self.defence_matrix = defence_matrix
        self.match_rng = match_rng
        self.match_engine_rng = match_engine_rng
        self.playable_primary_procedural_ids = tuple(
            dict.fromkeys(int(value) for value in playable_primary_procedural_ids)
        )
        self.playable_primary_club_ids = tuple(
            dict.fromkeys(int(value) for value in playable_primary_club_ids)
        )
        self.playable_country_allocation_plan = playable_country_allocation_plan
        self.human: HumanManagerState | None = None
        self.original_squad_membership = None
        self.pending_fixture_id: int | None = None
        self._pending_prior_results: tuple[tuple[int, object], ...] = ()
        self._pending_after_fixture_ids: tuple[int, ...] = ()
        self.pending_primary_entry: tuple | None = None
        self._pending_prior_primary_results: tuple[tuple[tuple, object], ...] = ()
        self._pending_after_primary_entries: tuple[tuple, ...] = ()
        self.last_transfer_executions: tuple[object, ...] = ()

    @classmethod
    def from_canonical_game_dir(
        cls,
        game_dir: str | Path,
        *,
        player_seed: int = 1,
        start_date: date = date(2000, 7, 4),
        match_engine_seed: int | None = None,
    ) -> "HumanGameplayController":
        """Create the same canonical shipped-data runtime used by Gates 5/6."""

        # Keep the initial canonical boundary limited to verification + parsing.
        # Schedule, GameState, coefficient and playable-scope materialization live
        # only in from_verified_canonical_database below.
        from fm2001_data import FM2001Database
        from verify import verify_canonical_files

        game_dir = Path(game_dir)
        verify_canonical_files(game_dir)
        database = FM2001Database(game_dir)
        return cls.from_verified_canonical_database(
            game_dir,
            database,
            player_seed=player_seed,
            start_date=start_date,
            match_engine_seed=match_engine_seed,
        )

    @classmethod
    def from_verified_canonical_database(
        cls,
        game_dir: str | Path,
        database,
        *,
        player_seed: int = 1,
        start_date: date = date(2000, 7, 4),
        match_engine_seed: int | None = None,
    ) -> "HumanGameplayController":
        """Materialize gameplay from an already verified canonical database.

        This is the heavy world/schedule boundary used after TeamSelect. The
        caller owns canonical-file verification and may reuse the exact parsed
        database that supplied the TeamSelect catalog, avoiding a second parse.
        """
        from canonical_matchday_audit import reconstruct_canonical_primary_schedule
        from competition_runtime import partition_root_procedural_league_ids
        from gate17_country_allocation_scope import (
            derive_playable_country_allocation_plan,
        )
        from gate17_full_scope_catalog import derive_original_playable_scope
        from gate17_playable_league_runtime_plan import (
            derive_playable_league_runtime_plan,
        )
        from match_coefficients import MatchCoefficientMatrices
        from season_regeneration import (
            partition_annual_type3_league_sources,
            required_annual_type3_sources,
        )

        game_dir = Path(game_dir)
        database_game_dir = Path(getattr(database, "game_dir", game_dir))
        if database_game_dir != game_dir:
            raise ValueError(
                "Verified canonical database does not belong to requested game directory"
            )
        playable_scope = derive_original_playable_scope(database)
        playable_runtime_plan = derive_playable_league_runtime_plan(
            playable_scope,
            database.competitions,
        )
        playable_country_allocation_plan = derive_playable_country_allocation_plan(
            playable_scope,
            database.league_allocation_records,
            database.competitions,
        )
        playable_primary_league_ids = (
            playable_runtime_plan.procedural_primary_competition_ids
        )
        playable_primary_club_ids = (
            playable_runtime_plan.primary_selectable_club_ids
        )
        english_primary_leagues, english_secondary_leagues = (
            partition_root_procedural_league_ids(
                database.competitions,
                country_region_id=26,
            )
        )
        if english_secondary_leagues:
            raise RuntimeError(
                "canonical English procedural League ownership changed: "
                f"secondary={english_secondary_leagues}"
            )
        annual_played_league_sources, _annual_dummy_league_sources = (
            partition_annual_type3_league_sources(
                database.competitions,
                database.cup_allocation_instructions,
            )
        )
        _annual_league_sources, annual_cup_sources = required_annual_type3_sources(
            database.competitions,
            database.cup_allocation_instructions,
        )
        annual_played_league_ids = tuple(
            int(competition_id)
            for competition_id in annual_played_league_sources
            if int(competition_id) != 0
        )
        annual_cup_child_league_ids = _annual_cup_child_procedural_ids(
            database.competitions,
            annual_cup_sources,
        )
        # Keep every TeamSelect-playable primary procedural League live, plus
        # the English promotion chain, every played annual ranking source and
        # every procedural League child needed to resolve an annual Cup source.
        # Secondary-container TeamSelect Leagues remain deliberately excluded.
        live_procedural_league_ids = tuple(dict.fromkeys(
            tuple(playable_primary_league_ids)
            + tuple(english_primary_leagues)
            + annual_played_league_ids
            + annual_cup_child_league_ids
        ))
        matrices = MatchCoefficientMatrices.from_executable(
            game_dir / "FOOTBAL.EXE"
        )
        primary_schedule = reconstruct_canonical_primary_schedule(database)
        state = GameState.from_database(
            database,
            start_date,
            seed=int(player_seed),
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(
            primary_schedule.premier_league_order
        )
        startup_rankings = dict(primary_schedule.ranked_source_club_ids)
        conference_two_ranking = startup_rankings.get(89)
        if conference_two_ranking is None:
            raise RuntimeError(
                "canonical Conference 2 ranking was not materialized"
            )
        for competition_id, ranking in startup_rankings.items():
            state.cup_results.replace_competition_ranking(
                int(competition_id),
                tuple(int(club_id) for club_id in ranking),
            )
        state.install_domestic_cup_primary_schedule(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.install_european_cup_primary_schedule(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.install_qualification_cup_primary_schedule(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.install_primary_matchday_order(
            primary_schedule.buckets,
            season_year=2000,
            procedural_league_ids=live_procedural_league_ids,
        )
        state.install_primary_schedule_shadow(
            primary_schedule.buckets,
            season_year=2000,
        )
        state.refresh_primary_procedural_leagues(live_procedural_league_ids)
        # This canonical fresh-world factory represents the original primary
        # pass before secondary scheduling. 404110(1) produces a first XI;
        # do not use prototype autofill or run this during save restoration.
        for club_id, club in state.clubs.items():
            if club.team_category_code == 1 and not club.name.startswith('!'):
                state.initialize_original_primary_first_season_squad(
                    club_id, primary_pass_before_secondary=True)
        return cls(
            state,
            matrices.attack,
            matrices.defence,
            MsvcCrtRng(primary_schedule.state_after),
            MatchEngineRng(
                int(time()) if match_engine_seed is None else int(match_engine_seed)
            ),
            playable_primary_procedural_ids=playable_primary_league_ids,
            playable_primary_club_ids=playable_primary_club_ids,
            playable_country_allocation_plan=playable_country_allocation_plan,
        )

    def playable_annual_progression_country_ids(self) -> tuple[int, ...]:
        plan = self.playable_country_allocation_plan
        if plan is None:
            return (26,)
        return tuple(int(country.country_id) for country in plan.countries)

    def preview_playable_country_season_transition(
        self,
        *,
        ranking_overrides=None,
    ):
        """Preview source-backed playable-country annual membership exchanges."""
        plan = self.playable_country_allocation_plan
        if plan is None:
            return self.state.preview_english_season_transition(
                ranking_overrides=ranking_overrides,
            )

        from gate17_playable_allocation_preview import (
            preview_playable_allocation_exchanges,
        )

        overrides = {
            int(competition_id): tuple(int(club_id) for club_id in ranking)
            for competition_id, ranking in (
                {} if ranking_overrides is None else ranking_overrides
            ).items()
        }
        endpoint_ids: list[int] = []
        seen: set[int] = set()
        for country in plan.countries:
            for raw_id in country.ranking_endpoint_ids:
                competition_id = int(raw_id)
                if competition_id not in seen:
                    endpoint_ids.append(competition_id)
                    seen.add(competition_id)

        rankings: dict[int, tuple[int, ...] | None] = {}
        for competition_id in endpoint_ids:
            ranking = overrides.get(competition_id)
            if ranking is None:
                ranking = self.state.season_transition_ranking(competition_id)
            rankings[competition_id] = (
                None
                if ranking is None
                else tuple(int(club_id) for club_id in ranking)
            )

        return preview_playable_allocation_exchanges(
            plan,
            self.state.league_allocation_records,
            rankings,
            self.state.club_competition_membership,
        )

    def regenerate_annual_primary_season(
        self,
        *,
        season_year: int | None = None,
        procedural_league_ids: Iterable[int] | None = None,
        full_playable_country_progression: bool = False,
    ):
        """Atomically roll the primary competition runtime into a new season.

        Qualification is captured from the completed old season before any
        membership exchange. The established default retains the recovered
        English transition. Gate-17 callers may explicitly request the exact
        TeamSelect-country allocation plan; that mode previews all required
        source exchanges fail-closed before the same atomic install. Annual
        competition construction and bucket shuffle
        then consume a cloned controller match_rng; only after the complete
        replacement validates are both GameState and the controller CRT state
        committed.
        """
        from competition_runtime import partition_root_procedural_league_ids
        from season_regeneration import (
            capture_annual_type3_qualification_snapshot,
            finalize_annual_dummy_league_rankings,
            materialize_annual_primary_schedule,
            partition_annual_type3_league_sources,
            required_annual_type3_sources,
        )

        if (
            self.pending_fixture_id is not None
            or self.pending_primary_entry is not None
            or self._pending_prior_results
            or self._pending_after_fixture_ids
            or self._pending_prior_primary_results
            or self._pending_after_primary_entries
        ):
            raise RuntimeError("cannot regenerate a season with a pending matchday")

        if season_year is None:
            season_year = int(self.state.calendar.current_date.year)
        season_year = int(season_year)

        competitions = tuple(self.state.competitions.values())
        rounds = tuple(self.state.round_definitions)
        clubs = tuple(self.state.clubs.values())
        countries = tuple(self.state.countries.values())
        allocations = tuple(self.state.cup_allocation_instructions)

        # DummyLeague rating reads runtime team roster order. Preserve each
        # club's current live order after transfers instead of falling back to
        # immutable Master.dat player ownership.
        ordered_players: list[object] = []
        seen_players: set[int] = set()
        for club_id in self.state.clubs:
            for player_id in self.state.club_roster_order.get(int(club_id), ()):
                player_id = int(player_id)
                player = self.state.players.get(player_id)
                if player is None or player_id in seen_players:
                    continue
                ordered_players.append(player)
                seen_players.add(player_id)
        for player_id, player in self.state.players.items():
            player_id = int(player_id)
            if player_id not in seen_players:
                ordered_players.append(player)
                seen_players.add(player_id)

        if procedural_league_ids is None:
            english_primary, english_secondary = (
                partition_root_procedural_league_ids(
                    competitions,
                    country_region_id=26,
                )
            )
            if english_secondary:
                raise RuntimeError(
                    "canonical English procedural League ownership changed: "
                    f"secondary={english_secondary}"
                )
            annual_played, _annual_dummy = partition_annual_type3_league_sources(
                competitions,
                allocations,
            )
            _annual_leagues, annual_cups = required_annual_type3_sources(
                competitions,
                allocations,
            )
            annual_played_ids = tuple(
                int(competition_id)
                for competition_id in annual_played
                if int(competition_id) != 0
            )
            annual_cup_child_ids = _annual_cup_child_procedural_ids(
                competitions,
                annual_cups,
            )
            procedural_league_ids = tuple(dict.fromkeys(
                tuple(int(value) for value in self.playable_primary_procedural_ids)
                + tuple(int(value) for value in english_primary)
                + annual_played_ids
                + annual_cup_child_ids
            ))
        else:
            procedural_league_ids = tuple(
                int(value) for value in procedural_league_ids
            )

        current_rng_state = getattr(self.match_rng, "state", None)
        if current_rng_state is None:
            raise TypeError("annual regeneration requires serializable match RNG state")
        trial_rng = MsvcCrtRng(int(current_rng_state))

        # 0x616A70 finalizes primary roots before LeagueAllocation movement.
        # DummyLeague +0x0C (0x4F7FE0) unconditionally invokes its RNG sorter,
        # so reproduce every primary DummyLeague finalization on the cloned CRT
        # stream before capturing qualification or previewing membership swaps.
        finalized_dummy_rankings = finalize_annual_dummy_league_rankings(
            trial_rng,
            competitions,
            countries,
            clubs,
            tuple(ordered_players),
            self.state.club_competition_membership,
        )
        qualification = capture_annual_type3_qualification_snapshot(
            self.state,
            competitions,
            allocations,
            ranking_overrides=finalized_dummy_rankings,
        )
        if full_playable_country_progression:
            transition = self.preview_playable_country_season_transition(
                ranking_overrides=finalized_dummy_rankings,
            )
        else:
            transition = self.state.preview_english_season_transition(
                ranking_overrides=finalized_dummy_rankings,
            )

        regeneration = materialize_annual_primary_schedule(
            trial_rng,
            competitions,
            rounds,
            clubs,
            countries,
            allocations,
            tuple(ordered_players),
            club_competition_membership=transition.memberships,
            season_year=season_year,
            qualification_rankings_by_competition=(
                qualification.qualification_rankings_by_competition
            ),
            cup_enumerated_club_ids_by_source=(
                qualification.cup_enumerated_club_ids_by_source
            ),
        )

        self.state.install_annual_primary_regeneration(
            regeneration,
            club_competition_membership=transition.memberships,
            procedural_league_ids=procedural_league_ids,
        )
        self.match_rng.seed(int(trial_rng.state))
        self.pending_fixture_id = None
        self._pending_prior_results = ()
        self._pending_after_fixture_ids = ()
        self.pending_primary_entry = None
        self._pending_prior_primary_results = ()
        self._pending_after_primary_entries = ()
        return regeneration

    def selectable_club_ids(self) -> tuple[int, ...]:
        """Return source-backed clubs whose required primary runtime is live."""
        fixed = tuple(
            int(value) for value in self.state.premier_league.club_ids
        )
        output: list[int] = []
        seen: set[int] = set()
        for club_id in fixed + tuple(self.playable_primary_club_ids):
            club_id = int(club_id)
            if club_id not in seen:
                output.append(club_id)
                seen.add(club_id)
        return tuple(output)

    def select_club(self, club_id: int) -> HumanManagerState:
        """Select one TeamSelect club backed by a live primary League owner."""

        if self.pending_fixture_id is not None or self.pending_primary_entry is not None:
            raise RuntimeError("cannot change club during a pending matchday")

        club_id = int(club_id)
        if club_id not in set(self.selectable_club_ids()):
            raise ValueError(
                f"club {club_id} is not in the supported primary TeamSelect scope"
            )
        if not self.state.ordered_club_roster(club_id):
            raise ValueError(f"club {club_id} has no runtime squad")

        membership = self.state.club_competition_membership.get(club_id)
        fixed_ids = {
            int(value) for value in self.state.premier_league.club_ids
        }
        if club_id not in fixed_ids:
            if membership is None:
                raise RuntimeError(
                    f"club {club_id} has no live League membership"
                )
            competition_id = int(membership)
            if competition_id not in set(self.playable_primary_procedural_ids):
                raise RuntimeError(
                    f"club {club_id} membership {competition_id} is not a "
                    "playable primary procedural League"
                )
            owner = self.state.procedural_leagues.get((competition_id, 0))
            if owner is None or club_id not in {
                int(value) for value in owner.club_ids
            }:
                raise RuntimeError(
                    f"club {club_id} has no materialized primary League owner"
                )

        membership = None
        if club_id in self.state.native_squad_first_formations:
            membership = self.state.construct_original_primary_squad_membership(club_id)
        self.human = HumanManagerState(club_id=club_id)
        self.original_squad_membership = membership
        if membership is not None:
            self.human.formation_id = self.state.native_squad_first_formations[club_id]
        club = self.state.clubs.get(club_id)
        if club is not None and hasattr(club, "starting_cash"):
            self.state.initialize_controlled_club_balance(club_id)
        else:
            # Lightweight synthetic databases may intentionally omit original
            # finance source fields.
            self.state.user_controlled_club_id = club_id
        self.state.initialize_controlled_stadium_source(club_id)
        return self.human

    def initialize_fresh_youth(self, option_mode: int | None = None):
        """Materialize the original separate fresh user youth list."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.initialize_fresh_user_youth(option_mode)

    def youth_players(self) -> tuple[object, ...]:
        """Return the current separate youth-list players in record order."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.user_youth_players()

    def promote_youth_player(
        self,
        player_id: int,
        *,
        weekly_wage: float,
        contract_months: int,
    ):
        """Apply the mapped EAMyouthpromoteplayer roster/contract transition."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.promote_user_youth_player(
            int(player_id),
            weekly_wage=float(weekly_wage),
            contract_months=int(contract_months),
        )

    def release_youth_player(self, player_id: int) -> bool:
        """Apply the mapped youth-list removal and free-player transition."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.release_user_youth_player(int(player_id))

    def _require_source_backed_fresh_financial_objective(self) -> None:
        if self.human is None:
            raise RuntimeError("select a human club first")
        club_id = int(self.human.club_id)
        balance = self.state.finance_balances.get(club_id)
        if balance is None or balance.financial_objective is None:
            competition_id = self.state.club_competition_membership.get(club_id)
            raise RuntimeError(
                "fresh chairman objective candidates are not source-backed for "
                f"controlled club {club_id} in competition {competition_id}"
            )

    def financial_objective_candidates(self) -> tuple[int, int, int]:
        """Return the source-backed fresh chairman objective choices."""
        self._require_source_backed_fresh_financial_objective()
        return self.state.financial_objective_candidates(self.human.club_id)

    def select_financial_objective(self, candidate_index: int) -> int | float:
        """Accept one source-backed chairman objective and replace live cash."""
        self._require_source_backed_fresh_financial_objective()
        return self.state.select_financial_objective(
            self.human.club_id,
            int(candidate_index),
        )

    def squad(self) -> tuple[object, ...]:
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.ordered_club_roster(self.human.club_id)

    def search_scouting_players(
        self,
        panel_state: ScoutingReseedState,
        *,
        candidate_predicate: Callable[[object], bool],
        sort_mode: int = 0,
        secondary_score_mode: int | None = None,
        secondary_caller_argument: int = 0,
        history_average_resolver: Callable[[object], float] | None = None,
        position_label_resolver: Callable[[object], str] | None = None,
        valuation_resolver: Callable[[object], float] | None = None,
    ) -> tuple[object, ...]:
        """Run the recovered UI-independent PScouting2K result pipeline.

        The original first-stage predicate contains several panel controls whose
        user-facing labels are still intentionally neutral. candidate_predicate
        is therefore explicit rather than replaced with guessed UI semantics.

        Sort modes 3 and 5 require their source values only when selected.
        Sort mode 2 reads RuntimePlayer's exact six-byte 0x41FB60 history by
        default; history_average_resolver remains available only as an explicit
        compatibility override. The five-state form_state is never substituted.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        sort_mode = int(sort_mode)
        if (
            sort_mode == SCOUTING_SORT_MODE_POSITION_LABEL
            and position_label_resolver is None
        ):
            raise ValueError("sort mode 3 requires position_label_resolver")
        if sort_mode == SCOUTING_SORT_MODE_VALUE and valuation_resolver is None:
            raise ValueError("sort mode 5 requires valuation_resolver")

        human_club_id = int(self.human.club_id)
        on_date = self.state.calendar.current_date

        # 0x4AE680 rejects either registered-club or current/temporary-club
        # membership in the controlled club before applying the panel filters.
        candidates = tuple(
            player
            for player in self.state.players.values()
            if int(player.club_id) != human_club_id
            and (
                player.loan_club_id is None
                or int(player.loan_club_id) != human_club_id
            )
        )

        def values_for(player) -> ScoutingSortValues:
            age = player.age(on_date)
            if age is None:
                if sort_mode == 1 or secondary_score_mode is not None:
                    raise ValueError(
                        f"player {player.index} has no usable date of birth"
                    )
                age = 0

            club_name = ""
            if sort_mode == SCOUTING_SORT_MODE_CLUB_NAME:
                club = self.state.clubs.get(int(player.club_id))
                if club is None or not hasattr(club, "name"):
                    raise ValueError(
                        f"player {player.index} has no source-backed club name"
                    )
                club_name = str(club.name)

            return ScoutingSortValues(
                # FILE_FORMATS.md maps runtime +0x0C=surname and +0x08=first.
                name_primary=str(player.surname),
                name_secondary=str(player.first_name),
                age=int(age),
                history_average=(
                    float(history_average_resolver(player))
                    if history_average_resolver is not None
                    else float(player.match_performance_average())
                ),
                position_label=(
                    str(position_label_resolver(player))
                    if position_label_resolver is not None
                    else ""
                ),
                club_name=club_name,
                valuation=(
                    float(valuation_resolver(player))
                    if valuation_resolver is not None
                    else 0.0
                ),
            )

        def rank_values_for(player) -> ScoutingRankValues:
            age = player.age(on_date)
            if age is None:
                raise ValueError(
                    f"player {player.index} has no usable date of birth"
                )
            return ScoutingRankValues(
                current_raw=tuple(player.current_raw),
                preferred_positions=tuple(player.positions),
                age=int(age),
            )

        return run_scouting_search(
            candidates,
            panel_state,
            candidate_predicate=candidate_predicate,
            sort_mode=sort_mode,
            sort_values=values_for,
            secondary_score_mode=secondary_score_mode,
            secondary_caller_argument=int(secondary_caller_argument),
            rank_values=rank_values_for if secondary_score_mode is not None else None,
        )

    def search_scouting_players_mapped(
        self,
        panel_state: ScoutingReseedState,
        *,
        page_mode: int,
        valuation_resolver: Callable[[object], float],
        scout_strength_min: int = 20,
        threshold_predicate: Callable[[object], bool] | None = None,
        selected_position_id: int | None = None,
        team_selector_predicate: Callable[[object], bool] | None = None,
        optional_position_predicate: Callable[[object], bool] | None = None,
        status_controls: ScoutingFilterControls = ScoutingFilterControls(),
        out_of_contract_resolver: Callable[[object], bool] | None = None,
        loan_listed_resolver: Callable[[object], bool] | None = None,
        loan_list_user_match_resolver: Callable[[object], bool] | None = None,
        sort_mode: int = 0,
        secondary_score_mode: int | None = None,
        secondary_caller_argument: int = 0,
        history_average_resolver: Callable[[object], float] | None = None,
        position_label_resolver: Callable[[object], str] | None = None,
    ) -> tuple[object, ...]:
        """Apply the mapped 0x4AE680 gates before the recovered result pipeline.

        Country-context mode, preferred-position membership and the Strengths
        threshold now come from live RuntimePlayer/GameState state. The original
        Strengths selector stores 0 for All and 1..17 for current_raw slots;
        scout_strength_min defaults to the shipped value 20. The optional
        predicate callbacks are retained only as additional caller constraints
        for compatibility. Out-of-contract status now comes from persistent
        RuntimePlayer state produced by the mapped monthly contract lifecycle;
        out_of_contract_resolver remains only as an explicit compatibility
        override.
        """

        if self.human is None:
            raise RuntimeError("select a human club first")

        on_date = self.state.calendar.current_date
        human_club = self.state.clubs.get(int(self.human.club_id))
        if human_club is None:
            raise ValueError("human-controlled club metadata is unavailable")
        active_country_id = int(getattr(human_club, "country_id"))
        active_competition_id = int(getattr(human_club, "competition_id"))
        countries_by_nationality = {
            int(getattr(country, "nationality_id")): country
            for country in self.state.countries.values()
        }

        def mapped_predicate(player) -> bool:
            # 0x4AE610 uses registered-club country whenever the player has
            # club context; only unattached players fall back to nationality.
            if int(player.club_id) >= 0:
                registered_club = self.state.clubs.get(int(player.club_id))
                if registered_club is None:
                    raise ValueError(
                        f"club metadata for player {int(player.index)} is unavailable"
                    )
                candidate_country_id = int(getattr(registered_club, "country_id"))
                candidate_country = self.state.countries.get(candidate_country_id)
            else:
                candidate_country = countries_by_nationality.get(
                    int(player.nationality_id)
                )
                candidate_country_id = (
                    int(getattr(candidate_country, "id"))
                    if candidate_country is not None
                    else -1
                )
            if candidate_country is None:
                raise ValueError(
                    f"country metadata for player {int(player.index)} is unavailable"
                )
            if not scouting_country_context_passes(
                int(panel_state.field_64e0),
                candidate_country_id=candidate_country_id,
                candidate_european_index=int(
                    getattr(candidate_country, "european_index")
                ),
                active_club_country_id=active_country_id,
            ):
                return False
            if (
                team_selector_predicate is not None
                and not bool(team_selector_predicate(player))
            ):
                return False

            age = player.age(on_date)
            if age is None:
                return False

            preferred_role = int(player.positions[0])
            position = self.state.positions.get(preferred_role)
            if position is None:
                raise ValueError(
                    f"position metadata for preferred role {preferred_role} is unavailable"
                )
            player_class = int(position.lineup_group)
            if not 0 <= player_class < 4:
                raise ValueError(
                    f"preferred role {preferred_role} has no scouting class"
                )

            return scouting_first_stage_passes(
                panel_state,
                ScoutingFilterValues(
                    age=int(age),
                    valuation=float(valuation_resolver(player)),
                    player_class=player_class,
                    transfer_listed=bool(player.transfer_listed),
                    out_of_contract=(
                        bool(out_of_contract_resolver(player))
                        if out_of_contract_resolver is not None
                        else bool(player.out_of_contract)
                    ),
                    loan_listed=(
                        bool(loan_listed_resolver(player))
                        if loan_listed_resolver is not None
                        else bool(player.loan_listed)
                    ),
                    loan_list_user_match=(
                        bool(loan_list_user_match_resolver(player))
                        if loan_list_user_match_resolver is not None
                        else (
                            registered_club is not None
                            and scouting_loan_list_user_match(
                                transfer_listed=bool(player.transfer_listed),
                                non_eu=bool(player.non_eu),
                                registered_club_competition_id=int(
                                    getattr(registered_club, "competition_id")
                                ),
                                active_club_competition_id=active_competition_id,
                            )
                        )
                    ),
                    team_selector_passes=True,
                    optional_position_passes=(
                        scouting_preferred_position_passes(
                            player.positions,
                            selected_position_id,
                        )
                        and (
                            optional_position_predicate is None
                            or bool(optional_position_predicate(player))
                        )
                    ),
                    threshold_passes=(
                        scouting_strength_threshold_passes(
                            player.current_raw,
                            int(panel_state.field_64e4),
                            int(scout_strength_min),
                        )
                        and (
                            threshold_predicate is None
                            or bool(threshold_predicate(player))
                        )
                    ),
                ),
                page_mode=int(page_mode),
                status_controls=status_controls,
            )

        return self.search_scouting_players(
            panel_state,
            candidate_predicate=mapped_predicate,
            sort_mode=int(sort_mode),
            secondary_score_mode=secondary_score_mode,
            secondary_caller_argument=int(secondary_caller_argument),
            history_average_resolver=history_average_resolver,
            position_label_resolver=position_label_resolver,
            valuation_resolver=(
                valuation_resolver
                if int(sort_mode) == SCOUTING_SORT_MODE_VALUE
                else None
            ),
        )

    def set_player_training_method(self, player_id: int, method_id: int) -> None:
        """Assign one of the seven original per-player training methods."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        player_id = int(player_id)
        player = self.state.players.get(player_id)
        if player is None or int(player.club_id) != int(self.human.club_id):
            raise ValueError("player is not in the human-controlled squad")
        player.set_training_method(int(method_id))

    def set_tactics(self, tactics: TeamTacticalState) -> None:
        if self.human is None:
            raise RuntimeError("select a human club first")
        self.state.set_team_tactics(self.human.club_id, tactics)

    def set_team_orders(self, orders: TeamOrderPriorities) -> None:
        if self.human is None:
            raise RuntimeError("select a human club first")
        self.human.team_orders = orders

    def set_current_cash(self, amount: int):
        """Initialize/update the selected club's live Balance current cash."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return self.state.set_current_cash(self.human.club_id, int(amount))

    def submit_cash_bid(
        self,
        target_player_id: int,
        cash_fee: int,
    ) -> LiveCashBidEvaluation:
        """Submit and evaluate one recovered ordinary cash-only transfer bid."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        return submit_live_cash_bid(
            self.state,
            target_player_id=int(target_player_id),
            buying_club_id=int(self.human.club_id),
            cash_fee=int(cash_fee),
        )

    def offer_player_contract(
        self,
        target_player_id: int,
        terms: ContractTerms,
        *,
        rng=None,
    ) -> OrdinaryMoneyResponseResult:
        """Submit player terms after the selling club accepted the cash bid.

        The method composes already recovered Gate-9 primitives. It does not
        invent the still-unmapped 0x422470 refusal/duration branches: those are
        returned explicitly by evaluate_ordinary_money_response.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        player_id = int(target_player_id)
        buyer_id = int(self.human.club_id)
        key = self.state.transfers.proposal_key(player_id, buyer_id)
        proposal = self.state.transfers.proposals.get(key)
        if proposal is None:
            raise RuntimeError("submit a cash bid for this player first")

        seller_response = evaluate_live_cash_bid(self.state, proposal)
        if seller_response.decision != SellingClubDecision.ACCEPTED:
            raise RuntimeError(
                f"selling club has not accepted the bid: "
                f"{seller_response.decision.value}"
            )

        if any(
            int(scheduled.proposal.target_player_id) == player_id
            and int(scheduled.proposal.buying_club_id) == buyer_id
            for scheduled in self.state.transfers.scheduled_transfers
        ):
            raise RuntimeError("this transfer is already scheduled")

        submitted = replace(proposal, contract_terms=terms)
        self.state.transfers.proposals[key] = submitted
        deal = self.state.transfers.deals.get(player_id)
        if deal is not None:
            deal.contract_terms = terms

        if rng is None:
            rng = self.match_rng
        result = evaluate_ordinary_money_response(
            self.state,
            submitted,
            rng,
        )

        self.state.transfers.proposals[key] = result.proposal
        if deal is not None:
            deal.contract_terms = result.proposal.contract_terms

        if result.outcome == OrdinaryMoneyResponse.ACCEPTED:
            schedule_ordinary_cash_transfer(
                self.state,
                result.proposal,
                mode=0,
            )
        return result

    def process_due_transfers(self):
        """Execute due transfers using the explicit Gate-10 affordability hook."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        results = execute_due_ordinary_cash_transfers(
            self.state,
            user_controlled_club_id=int(self.human.club_id),
        )
        self.last_transfer_executions = tuple(results)
        return self.last_transfer_executions

    def _procedural_league_owner_for_token(self, node_token: tuple):
        token = tuple(node_token)
        owners = tuple(
            live
            for live in self.state.procedural_leagues.values()
            if token in live.fixtures
        )
        if len(owners) != 1:
            if not owners:
                raise KeyError(token)
            raise RuntimeError(
                "procedural League node belongs to multiple live groups"
            )
        return owners[0]

    def _primary_entry_competition_id(self, entry: tuple) -> int:
        entry = tuple(entry)
        kind = entry[0]
        if kind == "premier_league":
            return 0
        if kind == "domestic_cup":
            return int(self.state.domestic_cups.node(tuple(entry[1])).competition_id)
        if kind == "european_cup":
            return int(self.state.european_cups.node(tuple(entry[1])).competition_id)
        if kind == "qualification_cup":
            return int(
                self.state.qualification_cups.node(tuple(entry[1])).competition_id
            )
        if kind == "procedural_league":
            return int(
                self._procedural_league_owner_for_token(
                    tuple(entry[1])
                ).competition_id
            )
        raise ValueError(f"unsupported primary match entry {entry!r}")

    def _human_selection_competition_id(self) -> int:
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is not None:
            return self._primary_entry_competition_id(
                self.pending_primary_entry
            )
        if self.pending_fixture_id is not None:
            return 0

        club_id = int(self.human.club_id)
        membership = self.state.club_competition_membership.get(club_id)
        if membership is not None:
            return int(membership)
        if (
            self.state.premier_league is not None
            and club_id in {
                int(value) for value in self.state.premier_league.club_ids
            }
        ):
            return 0
        raise RuntimeError(
            f"controlled club {club_id} has no live League membership"
        )

    def _human_selection_competition(self):
        competition_id = self._human_selection_competition_id()
        competition = self.state.competitions.get(int(competition_id))
        if competition is None:
            raise RuntimeError(
                f"human match competition {competition_id} is not loaded"
            )
        return competition

    def _human_live_league_table(self) -> tuple[object, ...]:
        if self.human is None:
            raise RuntimeError("select a human club first")
        club_id = int(self.human.club_id)
        competition_id = self.state.club_competition_membership.get(club_id)
        if competition_id is None:
            if (
                self.state.premier_league is not None
                and club_id in {
                    int(value) for value in self.state.premier_league.club_ids
                }
            ):
                competition_id = 0
            else:
                return ()

        competition_id = int(competition_id)
        if competition_id == 0:
            return tuple(self.state.premier_league_table())

        owners = tuple(
            live
            for (owner_competition_id, context), live
            in self.state.procedural_leagues.items()
            if int(owner_competition_id) == competition_id
            and int(context) == 0
        )
        if len(owners) > 1:
            raise RuntimeError(
                f"multiple root League owners for competition {competition_id}"
            )
        if not owners:
            return ()
        return tuple(owners[0].table())

    def _prepare_human_selection(
        self,
        formation_id: int,
        starter_ids: Iterable[int],
        substitute_ids: Iterable[int],
    ) -> PreparedAiMatchSelection:
        if self.human is None:
            raise RuntimeError("select a human club first")

        formation_id = int(formation_id)
        if not 0 <= formation_id < len(AI_FORMATIONS):
            raise ValueError("formation_id must be in 0..20")

        starters = tuple(int(value) for value in starter_ids)
        substitutes = tuple(int(value) for value in substitute_ids)
        if len(starters) != 11:
            raise ValueError("human lineup requires exactly 11 starters")

        competition = self._human_selection_competition()
        substitute_quota = resolved_substitute_quota(
            int(competition.substitute_quota)
        )
        if len(substitutes) != substitute_quota:
            raise ValueError(
                f"human lineup requires exactly {substitute_quota} substitutes"
            )

        all_selected = starters + substitutes
        if len(set(all_selected)) != len(all_selected):
            raise ValueError("human starters/substitutes must be unique")

        roster = self.state.ordered_club_roster(self.human.club_id)
        by_id = {int(player.index): player for player in roster}
        missing = tuple(player_id for player_id in all_selected if player_id not in by_id)
        if missing:
            raise ValueError(f"selected players are not in the human squad: {missing}")

        unavailable = tuple(
            player_id
            for player_id in all_selected
            if bool(by_id[player_id].base_match_unavailable)
        )
        if unavailable:
            raise ValueError(f"selected players are unavailable: {unavailable}")

        max_non_eu = int(competition.max_non_eu_players)
        selected_non_eu = sum(bool(by_id[player_id].non_eu) for player_id in all_selected)
        if selected_non_eu > max_non_eu:
            raise ValueError(
                f"human lineup contains {selected_non_eu} Non-EU players; "
                f"competition limit is {max_non_eu}"
            )

        for player in roster:
            player.clear_match_selection(reset_position=True)

        assignments: list[StarterAssignment] = []
        for player_id, slot in zip(starters, AI_FORMATIONS[formation_id]):
            player = by_id[player_id]
            player.assign_match_position(
                int(slot.role),
                int(slot.auxiliary_code),
            )
            player.set_match_active()
            assignments.append(
                StarterAssignment(
                    player_index=player_id,
                    role=int(slot.role),
                    auxiliary_code=int(slot.auxiliary_code),
                )
            )

        for player_id in substitutes:
            by_id[player_id].set_match_substitute_available()

        participants = collect_match_participants(
            self.human.club_id,
            roster,
        )
        if len(participants) != 11 + substitute_quota:
            raise RuntimeError("human participant collection did not match selection")

        return PreparedAiMatchSelection(
            lineup=AiLineupCoreResult(
                starters=tuple(assignments),
                substitutes=substitutes,
                unfilled_slot_indices=(),
            ),
            participants=tuple(participants),
            non_eu_restriction_relaxed=False,
        )

    def set_lineup(
        self,
        formation_id: int,
        starter_ids: Iterable[int],
        substitute_ids: Iterable[int],
    ) -> PreparedAiMatchSelection:
        """Persist the human XI/bench and apply it to live RuntimePlayer state."""

        selection = self._prepare_human_selection(
            formation_id,
            starter_ids,
            substitute_ids,
        )
        self.human.formation_id = int(formation_id)
        self.human.starter_ids = tuple(int(value) for value in starter_ids)
        self.human.substitute_ids = tuple(int(value) for value in substitute_ids)
        return selection

    def autofill_lineup(
        self,
        formation_id: int = 0,
    ) -> PreparedAiMatchSelection:
        """Choose a legal deterministic XI/bench using the proven selection core.

        This is a convenience for the temporary prototype and automated audits,
        not a replacement for manual human selection. It reuses the same
        evidence-backed slot/bench/Non-EU logic already used by AI selection,
        then persists the resulting player IDs as the human-controlled lineup.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")

        competition = self._human_selection_competition()

        roster = self.state.ordered_club_roster(self.human.club_id)
        selection = prepare_ai_match_selection(
            self.human.club_id,
            roster,
            int(formation_id),
            resolved_substitute_quota(int(competition.substitute_quota)),
            require_complete_xi=True,
            non_eu_limit=int(competition.max_non_eu_players),
        )
        starter_ids = tuple(
            int(assignment.player_index)
            for assignment in selection.lineup.starters
        )
        substitute_ids = tuple(
            int(player_id)
            for player_id in selection.lineup.substitutes
        )
        return self.set_lineup(
            int(formation_id),
            starter_ids,
            substitute_ids,
        )

    def drop_original_squad_row(self, source_index: int, target_index: int,
                                *, empty_row_index=None) -> bool:
        """Apply original row-name drop and retain the refreshed paired owner."""
        if self.human is None or self.original_squad_membership is None:
            raise RuntimeError('Original paired Squad owner is not retained')
        membership = self.original_squad_membership
        live_ids = tuple(p.index for p in self.state.ordered_club_roster(self.human.club_id))
        if (live_ids != tuple(p.player_id for p in membership.members)
                or any(self.state.players[m.player_id].match_selection_state_code != m.selection
                       or self.state.players[m.player_id].current_position != m.current_role
                       for m in membership.members)):
            raise RuntimeError('Original Squad drag owner is stale')
        refreshed = self.state.drop_original_primary_squad_row(self.human.club_id,
            source_index=source_index, target_index=target_index,
            empty_row_index=empty_row_index, substitute_quota=membership.substitute_quota)
        if refreshed is None:
            return False
        self.original_squad_membership = refreshed
        self._retain_original_squad_selected_ids()
        return True

    def _retain_original_squad_selected_ids(self):
        """Retain 510CD0's ordered live flags, never zip to AI formation slots."""
        if self.human is None:
            raise RuntimeError('Select a human club first')
        roster = self.state.ordered_club_roster(self.human.club_id)
        self.human.starter_ids = tuple(p.index for p in roster if p.match_active)
        self.human.substitute_ids = tuple(p.index for p in roster if p.match_substitute_available)

    def original_squad_match_selection(self) -> PreparedAiMatchSelection:
        """Read retained native human assignments without selection/role writes.

        Complete-input guards remain fail-closed. This is not prototype autofill
        and does not claim all original pre-match warning acceptance semantics.
        """
        if self.human is None or self.human.club_id not in self.state.native_squad_first_formations:
            raise RuntimeError('Native first-team formation has not been retained')
        roster = self.state.ordered_club_roster(self.human.club_id)
        if any(int(p.club_id) != self.human.club_id or p.loan_club_id is not None for p in roster):
            raise RuntimeError('Secondary-club native human selection is not integrated')
        starters = tuple(p for p in roster if p.match_active)
        substitutes = tuple(p for p in roster if p.match_substitute_available)
        competition = self._human_selection_competition()
        quota = resolved_substitute_quota(int(competition.substitute_quota))
        # Ordinary PBg 432190 -> 407FE0 -> 407C00(0) permits an underfilled
        # eligible bench; only its nonzero argument requires the exact quota.
        if len(starters) != 11 or len(substitutes) > quota:
            raise ValueError(f'Native human selection requires 11 starters and at most {quota} substitutes; '
                             f'retained {len(starters)} and {len(substitutes)}')
        if sum(p.current_position == 1 for p in starters) != 1:
            raise ValueError('Native human selection requires exactly one role-one starter')
        participants = collect_match_participants(self.human.club_id, roster)
        if (len(participants) != 11 + len(substitutes)
                or len({p.index for p in participants}) != len(participants)):
            raise RuntimeError('Native human participant ownership is incomplete')
        if any(p.base_match_unavailable for p in participants):
            raise ValueError('Native human selected player is unavailable')
        if sum(bool(p.non_eu) for p in participants) > int(competition.max_non_eu_players):
            raise ValueError('Native human selection exceeds the competition Non-EU limit')
        assignments = tuple(StarterAssignment(p.index, p.current_position, p.position_aux_code)
                            for p in starters)
        self._retain_original_squad_selected_ids()
        return PreparedAiMatchSelection(
            lineup=AiLineupCoreResult(assignments, tuple(p.index for p in substitutes), ()),
            participants=participants, non_eu_restriction_relaxed=False)

    def current_selection(self) -> PreparedAiMatchSelection:
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.human.club_id in self.state.native_squad_first_formations:
            return self.original_squad_match_selection()
        if not self.human.starter_ids:
            raise RuntimeError("set a human lineup first")
        return self._prepare_human_selection(
            self.human.formation_id,
            self.human.starter_ids,
            self.human.substitute_ids,
        )

    def _primary_entry_clubs(self, entry: tuple) -> tuple[int, int] | None:
        entry = tuple(entry)
        if entry[0] == "premier_league":
            fixture = self.state.premier_league.fixtures[int(entry[1])]
            return int(fixture.home_club_id), int(fixture.away_club_id)
        if entry[0] == "domestic_cup":
            node = self.state.domestic_cups.node(tuple(entry[1]))
            return node.resolve_pair(self.state.cup_results)
        if entry[0] == "european_cup":
            node = self.state.european_cups.node(tuple(entry[1]))
            return node.resolve_pair(self.state.cup_results)
        if entry[0] == "qualification_cup":
            node = self.state.qualification_cups.node(tuple(entry[1]))
            return node.resolve_pair(self.state.cup_results)
        if entry[0] == "procedural_league":
            token = tuple(entry[1])
            try:
                owner = self._procedural_league_owner_for_token(token)
            except (KeyError, RuntimeError):
                return None
            fixture = owner.fixtures[token]
            return int(fixture.home_club_id), int(fixture.away_club_id)
        raise ValueError(f"unsupported primary match entry {entry!r}")

    def _finish_shared_primary_day(self, had_results: bool) -> None:
        if (
            had_results
            and self.state.premier_league is not None
            and len(self.state.premier_league.results)
            == len(self.state.premier_league.fixtures)
        ):
            self.state.run_premier_league_financial_objective_season_transition()
        self.state.calendar.run_post_fixture_maintenance()
        controlled = None if self.human is None else self.human.club_id
        self.last_transfer_executions = tuple(
            self.state.run_due_transfer_maintenance(
                user_controlled_club_id=controlled,
            )
        )
        self.state.run_weekly_player_payroll()
        self.state.run_weekly_ai_transfer_maintenance(
            self.match_rng,
            user_controlled_club_id=controlled,
        )
        self.state.run_monthly_transfer_counter_reset()
        if self.state.finalize_single_user_sacking_control() is not None:
            self.human = None

    def _process_current_primary_day(self, *, native_primary_order=False):
        """Walk the retained primary order, suspending before human calculation.

        4A8260 -> 6168C0 -> LeagueMatch::513010 enters the pre-match modal
        inside this walk. Human calculation and post-fixture maintenance wait
        for its accepted choice; do not calculate then prompt. The native
        primary-League option finishes the first pass's AI entries beforehand.
        This reuses the existing bounded day-maintenance/calculator subset,
        not a claim that all original reschedule/event producers are integrated.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is not None:
            return self.pending_primary_entry
        due_order = self.state.primary_entries_due_today()
        if native_primary_order and due_order:
            # 6168EA/952 also gate on wrapper+8. A date/score search is NOT
            # proof that the native wrapper stayed unlinked after 4A7280.
            shadow = self.state.primary_schedule_shadow
            owners = shadow.days.get(self.state.calendar.current_date, ())
            for entry in due_order:
                matches = tuple(owner for owner in owners if (
                    owner.node_kind == 'fixed_league_match' and entry[0] == 'premier_league'
                    and owner.competition_id == 0 and owner.competition_context == 0
                    and len(owner.node_token) == 4 and owner.node_token[-1] == entry[1]
                ) or (
                    owner.node_kind == 'league_match' and entry[0] == 'procedural_league'
                    and owner.node_token == tuple(entry[1])
                ))
                if len(matches) != 1 or matches[0].wrapper_link_state != 'clear':
                    raise RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')
                direct = tuple(ref.direct_club_id for ref in matches[0].refs)
                if None in direct or direct != self._primary_entry_clubs(entry):
                    raise RuntimeError('Original NEXT current-day Side ownership is unresolved')
        human_due = []
        for entry in due_order:
            pair = self._primary_entry_clubs(entry)
            if pair is None:
                raise RuntimeError(f"Primary participant ownership is unresolved: {entry!r}")
            if native_primary_order:
                if entry[0] not in ('premier_league', 'procedural_league'):
                    raise RuntimeError('Original NEXT non-League day owner is not integrated')
                if any(getattr(self.state.clubs.get(club_id), 'team_category_code', None) != 1
                       for club_id in pair):
                    raise RuntimeError('Original NEXT requires source-qualified primary club sides')
            if self.human.club_id in pair:
                human_due.append(entry)
        if len(human_due) > 1:
            raise RuntimeError(
                f"expected at most one human primary match on "
                f"{self.state.calendar.current_date}, got {human_due}"
            )
        if not human_due:
            results = self.state.simulate_due_primary_ai_entries(
                self.attack_matrix, self.defence_matrix, self.match_rng,
                match_engine_rng=self.match_engine_rng,
            )
            self._finish_shared_primary_day(bool(results))
            return None

        human_entry = human_due[0]
        split = due_order.index(human_entry)
        # 6168C0 is TWO walks. For primary League sides 4037C0 is false;
        # 616990 skips human clubs on the first walk, so ALL ordinary AI
        # entries finish in source order before the second walk's human modal.
        # League +3C -> 5132E0 -> 511370 sets bit0, preventing AI replay.
        # Keep prototype skip-to-match's historical split separate.
        ai_entries = (tuple(entry for entry in due_order if entry != human_entry)
                      if native_primary_order else due_order[:split])
        prior = tuple(
            (entry, self.state.simulate_primary_ai_entry(
                entry, self.attack_matrix, self.defence_matrix, self.match_rng,
                match_engine_rng=self.match_engine_rng,
            ))
            for entry in ai_entries
        )
        self.pending_primary_entry = human_entry
        self._pending_prior_primary_results = prior
        self._pending_after_primary_entries = (() if native_primary_order
                                               else tuple(due_order[split + 1:]))
        return human_entry

    def advance_original_management_turn(
        self, *, next_match_date: date | None, selector_source_qualified: bool,
        container_end_date: date, turn_length: int = NATIVE_DEFAULT_TURN_LENGTH,
    ) -> OriginalManagementTurnOutcome:
        """Execute the native bounded NEXT target, not prototype skip-to-match.

        The caller must retain a real 615D10 selector/context; a missing
        header/fixture projection is not qualified null. No mode is selected
        here, no human match is calculated, and no future wrapper is declared
        clear after an unmodelled original runtime reschedule boundary.
        """
        if self.human is None:
            raise RuntimeError("select a human club first")
        target = original_management_advance_target(
            self.state.calendar.current_date, next_match_date=next_match_date,
            selector_source_qualified=selector_source_qualified,
            container_end_date=container_end_date, turn_length=turn_length,
        )
        if self.pending_primary_entry is not None:
            return OriginalManagementTurnOutcome(target, (), self.pending_primary_entry)
        # PBg's proven pre-match input guard is for tomorrow's fixture, not
        # permission to block a distant fixture-free turn on its current XI.
        # Warning acceptance remains separate; a rejection consumes no RNG.
        if next_match_date == self.state.calendar.current_date + timedelta(days=1):
            self.current_selection()
        processed = []
        for on_date in target.processing_dates:
            self.state.calendar.increment_one_day()
            self.state.invalidate_primary_schedule_wrapper_links()
            if self.state.calendar.current_date != on_date:
                raise RuntimeError("Original NEXT day owner diverged from its retained target")
            pending = self._process_current_primary_day(native_primary_order=True)
            processed.append(on_date)
            if pending is not None or self.human is None:
                break
        return OriginalManagementTurnOutcome(
            target, tuple(processed), self.pending_primary_entry,
        )

    def advance_to_next_user_primary_match(self):
        """Advance until a tagged PL/Cup match involving the human is pending."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is not None:
            return self.pending_primary_entry

        while True:
            future_dates = [
                on_date
                for on_date in self.state.primary_matchday_order
                if on_date > self.state.calendar.current_date
            ]
            future_dates.extend(
                node.scheduled_date
                for node in self.state.domestic_cups.nodes
                if node.node_token not in self.state.domestic_cups.completed_node_tokens
                and node.scheduled_date > self.state.calendar.current_date
            )
            future_dates.extend(
                node.scheduled_date
                for node in self.state.european_cups.nodes
                if node.node_token not in self.state.european_cups.completed_node_tokens
                and node.scheduled_date > self.state.calendar.current_date
            )
            future_dates.extend(
                node.scheduled_date
                for node in self.state.qualification_cups.nodes
                if node.node_token
                not in self.state.qualification_cups.completed_node_tokens
                and node.scheduled_date > self.state.calendar.current_date
            )
            if not future_dates:
                return None

            self.state.calendar.increment_one_day()
            self.state.invalidate_primary_schedule_wrapper_links()
            pending = self._process_current_primary_day()
            if pending is not None or self.human is None:
                return pending

    def play_user_primary_match(self) -> HumanPrimaryMatchdayOutcome:
        """Play the pending tagged PL/Cup/procedural-League match and finish its day."""
        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_primary_entry is None:
            raise RuntimeError("advance to a user primary match first")

        entry = self.pending_primary_entry
        selection = self.current_selection()
        if entry[0] == "premier_league":
            user_result = self.state.simulate_premier_league_human_fixture(
                int(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
                match_engine_rng=self.match_engine_rng,
                human_formation_id=self.human.formation_id,
            )
        elif entry[0] == "domestic_cup":
            user_result, _completion = self.state.simulate_domestic_cup_human_node(
                tuple(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
            )
        elif entry[0] == "european_cup":
            user_result, _completion = self.state.simulate_european_cup_human_node(
                tuple(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
            )
        elif entry[0] == "qualification_cup":
            user_result, _completion = (
                self.state.simulate_qualification_cup_human_node(
                    tuple(entry[1]),
                    self.human.club_id,
                    selection,
                    self.attack_matrix,
                    self.defence_matrix,
                    self.match_rng,
                    team_orders=self.human.team_orders,
                )
            )
        elif entry[0] == "procedural_league":
            user_result = self.state.simulate_procedural_league_human_node(
                tuple(entry[1]),
                self.human.club_id,
                selection,
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                team_orders=self.human.team_orders,
            )
        else:
            raise ValueError(f"unsupported human primary match entry {entry!r}")

        trailing = tuple(
            (
                trailing_entry,
                self.state.simulate_primary_ai_entry(
                    trailing_entry,
                    self.attack_matrix,
                    self.defence_matrix,
                    self.match_rng,
                match_engine_rng=self.match_engine_rng,
                ),
            )
            for trailing_entry in self._pending_after_primary_entries
        )
        all_results = (
            self._pending_prior_primary_results
            + ((entry, user_result),)
            + trailing
        )
        self._finish_shared_primary_day(bool(all_results))

        self.pending_primary_entry = None
        self._pending_prior_primary_results = ()
        self._pending_after_primary_entries = ()

        return HumanPrimaryMatchdayOutcome(
            match_entry=entry,
            user_result=user_result,
            matchday_results=all_results,
            table=self._human_live_league_table(),
        )

    def next_user_fixture(self):
        """Return the next unplayed PL fixture involving the human club."""

        if self.human is None:
            raise RuntimeError("select a human club first")

        current_date = self.state.calendar.current_date
        candidates = []
        for fixture in self.state.premier_league.fixtures.values():
            if int(fixture.id) in self.state.premier_league.results:
                continue
            if self.human.club_id not in (
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            ):
                continue
            fixture_date = self.state.premier_league.round_date(
                int(fixture.round_index)
            )
            if fixture_date is None or fixture_date < current_date:
                continue
            candidates.append((fixture_date, int(fixture.id), fixture))

        if not candidates:
            return None
        return min(candidates, key=lambda item: (item[0], item[1]))[2]

    def advance_to_next_user_fixture(self):
        """Advance autonomously until the human fixture is next to execute.

        Earlier fixtures on the same date are simulated in exact installed
        scheduler order. Later same-day fixtures remain pending until after the
        user fixture, preserving 0x615C10-style matchday order and ensuring
        daily maintenance still runs only after every fixture on that date.
        """

        if self.pending_fixture_id is not None:
            return self.state.premier_league.fixtures[self.pending_fixture_id]

        fixture = self.next_user_fixture()
        if fixture is None:
            return None
        target_date = self.state.premier_league.round_date(
            int(fixture.round_index)
        )
        if target_date is None:
            raise RuntimeError("human fixture has no reconstructed round date")

        while self.state.calendar.current_date + timedelta(days=1) < target_date:
            self.state.advance_one_day_with_premier_league_ai_fixtures(
                self.attack_matrix,
                self.defence_matrix,
                self.match_rng,
                match_engine_rng=self.match_engine_rng,
            )

        if self.state.calendar.current_date < target_date:
            self.state.calendar.increment_one_day()

        due_order = self.state.due_premier_league_fixture_ids_in_scheduler_order()
        human_due = tuple(
            fixture_id
            for fixture_id in due_order
            if self.human.club_id
            in (
                int(self.state.premier_league.fixtures[fixture_id].home_club_id),
                int(self.state.premier_league.fixtures[fixture_id].away_club_id),
            )
        )
        if len(human_due) != 1:
            raise RuntimeError(
                f"expected exactly one human fixture on {target_date}, got {human_due}"
            )

        human_fixture_id = human_due[0]
        split = due_order.index(human_fixture_id)
        prior_results = []
        for fixture_id in due_order[:split]:
            prior_results.append(
                (
                    fixture_id,
                    self.state.simulate_premier_league_ai_fixture(
                        fixture_id,
                        self.attack_matrix,
                        self.defence_matrix,
                        self.match_rng,
                    match_engine_rng=self.match_engine_rng,
                    ),
                )
            )

        self.pending_fixture_id = human_fixture_id
        self._pending_prior_results = tuple(prior_results)
        self._pending_after_fixture_ids = tuple(due_order[split + 1 :])
        return self.state.premier_league.fixtures[human_fixture_id]

    def play_user_fixture(self) -> HumanMatchdayOutcome:
        """Play the pending human fixture, finish the matchday, and return state."""

        if self.human is None:
            raise RuntimeError("select a human club first")
        if self.pending_fixture_id is None:
            raise RuntimeError("advance to a user fixture first")

        selection = self.current_selection()
        fixture_id = int(self.pending_fixture_id)
        user_result = self.state.simulate_premier_league_human_fixture(
            fixture_id,
            self.human.club_id,
            selection,
            self.attack_matrix,
            self.defence_matrix,
            self.match_rng,
            team_orders=self.human.team_orders,
            match_engine_rng=self.match_engine_rng,
            human_formation_id=self.human.formation_id,
        )

        trailing = []
        for ai_fixture_id in self._pending_after_fixture_ids:
            trailing.append(
                (
                    int(ai_fixture_id),
                    self.state.simulate_premier_league_ai_fixture(
                        int(ai_fixture_id),
                        self.attack_matrix,
                        self.defence_matrix,
                        self.match_rng,
                    match_engine_rng=self.match_engine_rng,
                    ),
                )
            )

        all_results = (
            self._pending_prior_results
            + ((fixture_id, user_result),)
            + tuple(trailing)
        )
        # Matchday completion is the clean-room counterpart of the annual
        # competition-finalization boundary. Only the final PL matchday can
        # trigger the recovered sporting/financial objective transition.
        if (
            all_results
            and len(self.state.premier_league.results)
            == len(self.state.premier_league.fixtures)
        ):
            self.state.run_premier_league_financial_objective_season_transition()
        self.state.calendar.run_post_fixture_maintenance()
        self.last_transfer_executions = tuple(
            self.state.run_due_transfer_maintenance(
                user_controlled_club_id=self.human.club_id,
            )
        )
        self.state.run_weekly_player_payroll()
        self.state.run_weekly_ai_transfer_maintenance(
            self.match_rng,
            user_controlled_club_id=self.human.club_id,
        )
        self.state.run_monthly_transfer_counter_reset()

        # DBRUser +0x10D8 is consumed by the outer manager loop after the
        # reason-specific sacking message is queued. In single-user play the
        # original then leaves management for PStartMenu. Preserve the state,
        # but end active human control only after this matchday's maintenance.
        sacking_reason = self.state.finalize_single_user_sacking_control()
        if sacking_reason is not None:
            self.human = None

        self.pending_fixture_id = None
        self._pending_prior_results = ()
        self._pending_after_fixture_ids = ()

        return HumanMatchdayOutcome(
            fixture_id=fixture_id,
            user_result=user_result,
            matchday_results=all_results,
            table=tuple(self.state.premier_league_table()),
        )
