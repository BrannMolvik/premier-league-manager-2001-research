import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import runtime_layout


class RuntimeLayoutTests(unittest.TestCase):
    def test_source_run_uses_repository_root(self):
        with (
            patch.object(sys, "_MEIPASS", None, create=True),
            patch.object(sys, "frozen", False, create=True),
        ):
            self.assertEqual(
                runtime_layout.application_root(),
                Path(runtime_layout.__file__).resolve().parent.parent,
            )

    def test_onefile_prefers_meipass_resource_root(self):
        with (
            patch.object(sys, "_MEIPASS", "C:/Temp/fm2001-bundle", create=True),
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", "C:/Apps/FM2001/FM2001-Windows11.exe"),
        ):
            self.assertEqual(
                runtime_layout.application_root(),
                Path("C:/Temp/fm2001-bundle").resolve(),
            )

    def test_frozen_onedir_uses_executable_parent_without_meipass(self):
        with (
            patch.object(sys, "_MEIPASS", None, create=True),
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", "C:/Apps/FM2001/FM2001-Windows11.exe"),
        ):
            self.assertEqual(
                runtime_layout.application_root(),
                Path("C:/Apps/FM2001/FM2001-Windows11.exe").resolve().parent,
            )


if __name__ == "__main__":
    unittest.main()
