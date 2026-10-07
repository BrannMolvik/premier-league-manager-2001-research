import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from development_playtest import DevelopmentPlaytestSession
import test_human_gameplay as human_fixtures
import test_internal_save as save_fixtures


class DevelopmentPlaytestTests(unittest.TestCase):
    def test_full_roster_is_not_the_original_hosts_twenty_row_slice(self):
        rows = tuple(range(30))
        session = DevelopmentPlaytestSession(object(), object())
        with patch('development_playtest.ManagementSourceDataBridge') as bridge:
            bridge.return_value.squad_rows.return_value = rows
            self.assertEqual(session.roster(), rows)

    def test_selectable_clubs_are_from_live_runtime_not_premier_only(self):
        c = SimpleNamespace(state=SimpleNamespace(clubs={1:SimpleNamespace(name='PL'),
            349:SimpleNamespace(name='Southport')}), selectable_club_ids=lambda:(1,349))
        self.assertEqual(DevelopmentPlaytestSession(c, None).clubs(), ((1,'PL'),(349,'Southport')))

    def test_advance_and_play_use_tagged_primary_workflow_and_actual_league(self):
        c, token = human_fixtures.HumanGameplayControllerTests().build_primary_procedural_controller()
        session = DevelopmentPlaytestSession(c, None)
        session.select(21)
        c.autofill_lineup()
        self.assertEqual(session.substitute_quota(), 3)
        self.assertEqual(session.advance(), ('procedural_league',token))
        outcome = session.play()
        self.assertEqual(outcome.match_entry, ('procedural_league',token))
        self.assertEqual({row.club_id for row in session.table()}, {21,22})
        self.assertIsNone(session.pending_names())

    def test_pending_names_use_explicit_fixture_participants(self):
        c = SimpleNamespace(pending_primary_entry=('fixture',42),
            _primary_entry_clubs=lambda entry:(12,13),
            state=SimpleNamespace(clubs={12:SimpleNamespace(name='Home'),13:SimpleNamespace(name='Away')}))
        self.assertEqual(DevelopmentPlaytestSession(c,None).pending_names(), ('Home','Away'))
        c._primary_entry_clubs = lambda entry: None
        with self.assertRaisesRegex(RuntimeError,'no resolved participants'):
            DevelopmentPlaytestSession(c,None).pending_names()

    def test_disk_save_reload_preserves_lineup_and_does_not_need_controller_db(self):
        c = save_fixtures.InternalSaveTests().build_controller()
        session = DevelopmentPlaytestSession(c, save_fixtures.Database())
        expected = c.human.starter_ids
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'playtest.fm2k'
            session.save(path)
            session.load(path)
            self.assertIsNot(session.controller, c)
            self.assertEqual(session.controller.human.starter_ids, expected)
            previous = session.controller
            with self.assertRaises(FileNotFoundError):
                session.load(Path(directory)/'absent.fm2k')
            self.assertIs(session.controller, previous)


if __name__ == '__main__':
    unittest.main()
