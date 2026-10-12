import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from playtest_distribution import prepare_playtest
from gate17_package_candidate import PackageCandidateError


class PlaytestDistributionTests(unittest.TestCase):
    def test_direct_layout_identity_launcher_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exe = root / 'FM2001-Windows11.exe'
            exe.write_bytes(b'fixture-executable')
            with patch('playtest_distribution.validate_distribution') as validate:
                receipt = prepare_playtest(root, 'a' * 40)
            validate.assert_called_once_with(root, exe.name)
            self.assertEqual(receipt['repository_commit'], 'a' * 40)
            self.assertLessEqual(receipt['max_extracted_path_length'], 240)
            self.assertEqual(receipt, json.loads((root / 'PLAYTEST-MANIFEST.json').read_text()))
            for entry in receipt['files']:
                self.assertEqual(entry['sha256'], hashlib.sha256((root / entry['path']).read_bytes()).hexdigest())
            launcher = (root / 'PLAYTEST.cmd').read_text()
            self.assertIn('--skip-startup-media', launcher)
            self.assertNotIn('--prototype-ui', launcher)
            self.assertIn('videos', launcher)

    def test_bad_commit_and_long_paths_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                prepare_playtest(root, 'main')
            deep = root / ('x' * 100) / ('y' * 100) / ('z' * 40)
            with patch('playtest_distribution.validate_distribution'), patch.object(Path, 'rglob', return_value=iter([deep])), self.assertRaises(ValueError):
                prepare_playtest(root, 'a' * 40)
            self.assertFalse((root / 'PLAYTEST.cmd').exists())

    def test_existing_distribution_verification_is_not_bypassed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PackageCandidateError):
                prepare_playtest(directory, 'a' * 40)
