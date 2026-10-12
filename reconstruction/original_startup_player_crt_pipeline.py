"""Explicit first two FM2001 startup CRT stages on ONE owned RNG.

Native application startup 0x531098/0x53109E seeds CRT once. The first
Loader444 block consumes 260 raw rand calls; original DBTPlayers then
constructs all players and loads their records using the same stream.

This source-bounded adapter is NOT a complete original new-game startup,
does not infer OS time, prove first-Loader444 occurrence, or execute the
later TeamSelect/queue/manager/user/match stages. Only call it from a
genuinely source-qualified application bootstrap; the canonical GUI is
not currently wired to this adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from match_schedule import MsvcCrtRng
from startup_rng import (
    LOADER444_FIRST_DECODE_RAW_DRAWS,
    consume_loader444_first_decode_rng,
)

if TYPE_CHECKING:
    from game_state import GameState


class OriginalStartupCrtPhaseError(RuntimeError):
    """Original source-backed startup stage was missing, repeated, or wrong."""


@dataclass(frozen=True)
class OriginalStartupCrtPhaseReceipt:
    owner_seed_checkpoint: int
    after_first_loader444: int
    after_dbtplayers: int
    raw_first_loader444_draw_count: int
    materialized_player_count: int
    full_native_startup_verified: bool = False


class OriginalStartupPlayerCrtPipeline:
    """Owns the exact provided CRT; prevents two copies of the startup draw.

    Does NOT seed an alternate stream, skip Loader444, use the state-only
    DBTPlayers replay and then construct actual players a second time, or
    silently restart after a partly-consumed GameState construction fails.
    """

    def __init__(self, source_application_crt: MsvcCrtRng):
        if type(source_application_crt) is not MsvcCrtRng:
            raise TypeError("Require source-owned MsvcCrtRng instance")
        self.rng = source_application_crt
        self._phase = "application_seeded"
        self._initial_checkpoint = source_application_crt.state
        self._loader_checkpoint: int | None = None
        self._receipt: OriginalStartupCrtPhaseReceipt | None = None
        self.game_state: GameState | None = None

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def receipt(self) -> OriginalStartupCrtPhaseReceipt | None:
        return self._receipt

    def consume_first_loader444_decode(self) -> int:
        if self._phase != "application_seeded":
            raise OriginalStartupCrtPhaseError(
                "Original first Loader444 decode must run once before DBTPlayers"
            )
        # Set the failure state BEFORE consuming, so exception cannot cause
        # an unqualified replay of a partially advanced native CRT.
        self._phase = "unqualified"
        n = consume_loader444_first_decode_rng(self.rng)
        if n != LOADER444_FIRST_DECODE_RAW_DRAWS:
            raise OriginalStartupCrtPhaseError(
                "Native Loader444 first-decode raw draw count changed"
            )
        self._loader_checkpoint = self.rng.state
        self._phase = "loader444_decoded"
        return n

    def materialize_dbtplayers(
        self, database, start_date: date, *, season_year: int | None = None
    ) -> GameState:
        if self._phase != "loader444_decoded":
            raise OriginalStartupCrtPhaseError(
                "DBTPlayers requires prior first Loader444 on the same CRT"
            )
        # Defer import until player materialization. Failed constructors may
        # have advanced CRT: do NOT pretend it can be rolled back/retried.
        from game_state import GameState

        self._phase = "unqualified"
        state = GameState.from_database(
            database, start_date,
            source_shared_crt=self.rng,
            season_year=season_year,
        )
        if state.rng is not self.rng:
            raise OriginalStartupCrtPhaseError(
                "DBTPlayers unexpectedly substituted its source CRT owner"
            )
        self.game_state = state
        self._receipt = OriginalStartupCrtPhaseReceipt(
            owner_seed_checkpoint=self._initial_checkpoint,
            after_first_loader444=self._loader_checkpoint,
            after_dbtplayers=self.rng.state,
            raw_first_loader444_draw_count=LOADER444_FIRST_DECODE_RAW_DRAWS,
            materialized_player_count=len(state.players),
        )
        self._phase = "players_materialized"
        return state
