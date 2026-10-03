"""Tests for source-closed FastView PlayerProxy history access."""
from pathlib import Path
import unittest

from gate14_fastview_player_history import (
    SOURCE_DBRPLAYER_CONDITION_OFFSET,
    SOURCE_DBRPLAYER_FORM_STATE_OFFSET,
    SOURCE_ENERGY_DERIVER_VA,
    SOURCE_ENERGY_WRAPPER_VA,
    SOURCE_FORM_HISTORY_GETTER_VA,
    SOURCE_FORM_WRAPPER_VA,
    SOURCE_HISTORY_SAMPLE_COUNT,
    SOURCE_PLAYER_PROXY_UPDATE_VA,
    FastViewPlayerHistories,
    FastViewPlayerHistoryError,
    derive_fastview_energy,
    player_history_sample_index,
    source_history_byte_offset,
)


class FastViewPlayerHistoryTests(unittest.TestCase):
    def _histories(self):
        condition = tuple(max(70, 100 - index) for index in range(24))
        form = (5, 6, 6, 4, 4, 5) + (5,) * 18
        return FastViewPlayerHistories(condition, form)

    def test_source_addresses_and_persistent_fields_are_locked(self):
        self.assertEqual(SOURCE_PLAYER_PROXY_UPDATE_VA, 0x5247A0)
        self.assertEqual(SOURCE_FORM_WRAPPER_VA, 0x632FC0)
        self.assertEqual(SOURCE_FORM_HISTORY_GETTER_VA, 0x6308B0)
        self.assertEqual(SOURCE_ENERGY_WRAPPER_VA, 0x633000)
        self.assertEqual(SOURCE_ENERGY_DERIVER_VA, 0x630910)
        self.assertEqual(SOURCE_DBRPLAYER_CONDITION_OFFSET, 0x77)
        self.assertEqual(SOURCE_DBRPLAYER_FORM_STATE_OFFSET, 0x192)

    def test_history_index_clamps_at_source_tick_119(self):
        self.assertEqual(player_history_sample_index(0), 0)
        self.assertEqual(player_history_sample_index(4), 0)
        self.assertEqual(player_history_sample_index(5), 1)
        self.assertEqual(player_history_sample_index(119), 23)
        self.assertEqual(player_history_sample_index(120), 23)
        self.assertEqual(player_history_sample_index(900), 23)

    def test_exact_match_record_offsets_preserve_two_adjacent_histories(self):
        self.assertEqual(source_history_byte_offset(0, 0, 0, form=False), 0x4C)
        self.assertEqual(source_history_byte_offset(0, 0, 0, form=True), 0x64)
        self.assertEqual(source_history_byte_offset(0, 1, 0, form=False), 0x98)
        self.assertEqual(source_history_byte_offset(0, 1, 0, form=True), 0xB0)
        self.assertEqual(source_history_byte_offset(1, 0, 0, form=False), 0x5FC)
        self.assertEqual(source_history_byte_offset(1, 0, 0, form=True), 0x614)
        self.assertEqual(source_history_byte_offset(1, 2, 10, form=False), 0x696)
        self.assertEqual(source_history_byte_offset(1, 2, 10, form=True), 0x6AE)

    def test_form_display_reads_match_form_history_not_persistent_form_state(self):
        histories = self._histories()
        self.assertEqual(histories.form_at_tick(0), 5)
        self.assertEqual(histories.form_at_tick(5), 6)
        self.assertEqual(histories.form_at_tick(10), 6)
        self.assertEqual(histories.form_at_tick(15), 4)

    def test_energy_deriver_matches_source_trend_rng_and_condition_cap(self):
        histories = self._histories()

        # tick 5: no trend iteration; 100 + (3-3), capped by condition[1]=99.
        self.assertEqual(derive_fastview_energy(histories, 5, 3), 99)

        # tick 11 compares form 5 vs 0 (rise => -4), then 10 vs 5
        # (not rise => +4), so baseline returns to 100; roll 2 => 99;
        # cap uses first boundary >=11 (15 -> condition[3]=97).
        self.assertEqual(derive_fastview_energy(histories, 11, 2), 97)

        low = FastViewPlayerHistories((1,) * 24, (5,) * 24)
        self.assertEqual(derive_fastview_energy(low, 5, 0), 1)

    def test_invalid_histories_or_rng_fail_closed(self):
        with self.assertRaises(FastViewPlayerHistoryError):
            FastViewPlayerHistories((100,) * 23, (5,) * 24)
        with self.assertRaises(FastViewPlayerHistoryError):
            FastViewPlayerHistories((100,) * 24, (0,) * 24)
        with self.assertRaises(FastViewPlayerHistoryError):
            derive_fastview_energy(self._histories(), 5, 6)
        with self.assertRaises(FastViewPlayerHistoryError):
            source_history_byte_offset(2, 0, 0, form=False)

    def test_history_contract_does_not_import_simulation_or_rng(self):
        source = Path(__file__).with_name(
            "gate14_fastview_player_history.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "random",
            "human_gameplay",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
