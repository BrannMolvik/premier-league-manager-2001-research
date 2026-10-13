"""Verify Loader444 then real DBTPlayers on one seeded source CRT.

These are explicit source-stage tests, not actual original GUI/Win11
acceptance or a fully observed seed-to-click startup trace.
"""
import unittest
from dataclasses import dataclass
from datetime import date

from match_schedule import MsvcCrtRng
from startup_rng import (
    LOADER444_FIRST_DECODE_RAW_DRAWS,
    consume_loader444_first_decode_rng,
    consume_dbtplayers_startup_rng,
)
from original_startup_player_crt_pipeline import (
    OriginalStartupPlayerCrtPipeline,
    OriginalStartupCrtPhaseError,
)


@dataclass(frozen=True)
class FakePlayer:
    index: int
    club_id: int
    first_name: str = "A"
    surname: str = "P"
    nationality_id: int = 0
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 1
    height_cm: int = 180
    weight_kg: int = 75
    positions: tuple[int, int, int] = (0, 0, 0)
    current_raw: tuple[int, ...] = (100,) * 17
    target_raw: tuple[int, ...] = (150,) * 17


class FakeDatabase:
    players = (FakePlayer(1, 1), FakePlayer(2, 2))
    real_fixtures = ()


class OriginalStartupPlayerCrtPipelineTests(unittest.TestCase):
    def test_exact_loader_then_real_dbtplayers_match_state_only_source_phase(self):
        reference = MsvcCrtRng(1234)
        self.assertEqual(
            consume_loader444_first_decode_rng(reference),
            LOADER444_FIRST_DECODE_RAW_DRAWS,
        )
        after_loader = reference.state
        self.assertEqual(consume_dbtplayers_startup_rng(reference, 2), 12)
        after_players = reference.state

        rng = MsvcCrtRng(1234)
        pipeline = OriginalStartupPlayerCrtPipeline(rng)
        self.assertEqual(pipeline.consume_first_loader444_decode(), 260)
        self.assertEqual(rng.state, after_loader)
        game = pipeline.materialize_dbtplayers(
            FakeDatabase(), date(2000, 8, 18), season_year=2000,
        )
        self.assertIs(game.rng, rng)
        self.assertIs(pipeline.game_state, game)
        self.assertEqual(rng.state, after_players)
        self.assertEqual(pipeline.phase, "players_materialized")
        self.assertEqual(pipeline.receipt.owner_seed_checkpoint, 1234)
        self.assertEqual(pipeline.receipt.after_first_loader444, after_loader)
        self.assertEqual(pipeline.receipt.after_dbtplayers, after_players)
        self.assertEqual(pipeline.receipt.materialized_player_count, 2)
        self.assertFalse(pipeline.receipt.full_native_startup_verified)
        self.assertEqual(game._resolve_rng().rand15(), reference.rand15())

    def test_rejects_repeated_or_out_of_order_phases_without_advancing_rng(self):
        rng = MsvcCrtRng(1)
        pipeline = OriginalStartupPlayerCrtPipeline(rng)
        with self.assertRaises(OriginalStartupCrtPhaseError):
            pipeline.materialize_dbtplayers(FakeDatabase(), date(2000, 8, 18))
        self.assertEqual(pipeline.phase, "application_seeded")
        self.assertEqual(rng.state, 1)
        pipeline.consume_first_loader444_decode()
        after_loader = rng.state
        for bad in (pipeline.consume_first_loader444_decode,):
            with self.assertRaises(OriginalStartupCrtPhaseError):
                bad()
        self.assertEqual(rng.state, after_loader)
        pipeline.materialize_dbtplayers(FakeDatabase(), date(2000, 8, 18))
        after_players = rng.state
        with self.assertRaises(OriginalStartupCrtPhaseError):
            pipeline.consume_first_loader444_decode()
        with self.assertRaises(OriginalStartupCrtPhaseError):
            pipeline.materialize_dbtplayers(FakeDatabase(), date(2000, 8, 18))
        self.assertEqual(rng.state, after_players)

    def test_source_crt_owner_type_is_strict(self):
        for fake in (1, None, True, object(), "1"):
            with self.subTest(fake=fake), self.assertRaises(TypeError):
                OriginalStartupPlayerCrtPipeline(fake)

    def test_failed_player_construction_never_claims_completed_or_retryable_phase(self):
        rng = MsvcCrtRng(13)
        pipeline = OriginalStartupPlayerCrtPipeline(rng)
        pipeline.consume_first_loader444_decode()
        class MissingPlayerDatabase:
            pass
        with self.assertRaises((AttributeError, TypeError)):
            pipeline.materialize_dbtplayers(
                MissingPlayerDatabase(), date(2000, 8, 18),
            )
        self.assertEqual(pipeline.phase, "unqualified")
        self.assertIsNone(pipeline.receipt)
        self.assertIsNone(pipeline.game_state)
        with self.assertRaises(OriginalStartupCrtPhaseError):
            pipeline.materialize_dbtplayers(FakeDatabase(), date(2000, 8, 18))


if __name__ == "__main__":
    unittest.main()
