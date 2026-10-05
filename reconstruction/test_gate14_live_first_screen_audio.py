from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from gate14_live_first_screen_audio import (
    CANONICAL_MENUS_RELATIVE_PATH,
    Gate14LiveFirstScreenAudioError,
    install_live_first_screen_audio,
    load_canonical_menus_bnk,
)


class Gate14LiveFirstScreenAudioTests(unittest.TestCase):
    def test_non_windows_host_is_left_unmodified(self):
        host = object()
        backend_factory = Mock()
        with patch(
            "gate14_live_first_screen_audio.load_canonical_menus_bnk"
        ) as load:
            result = install_live_first_screen_audio(
                host,
                Path("/game"),
                platform_system="Linux",
                backend_factory=backend_factory,
            )
        self.assertIsNone(result)
        load.assert_not_called()
        backend_factory.assert_not_called()

    def test_missing_or_noncanonical_bank_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(
                Gate14LiveFirstScreenAudioError,
                "could not be read",
            ):
                load_canonical_menus_bnk(root)

            path = root / CANONICAL_MENUS_RELATIVE_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(b"not-the-canonical-bank")
            with self.assertRaisesRegex(
                Gate14LiveFirstScreenAudioError,
                "does not match",
            ):
                load_canonical_menus_bnk(root)

    def test_windows_path_composes_verified_bank_backend_and_binding(self):
        host = object()
        backend = object()
        backend_factory = Mock(return_value=backend)
        binding = object()
        with patch(
            "gate14_live_first_screen_audio.load_canonical_menus_bnk",
            return_value=b"verified-bank",
        ) as load, patch(
            "gate14_live_first_screen_audio.install_first_screen_press_audio",
            return_value=binding,
        ) as install:
            result = install_live_first_screen_audio(
                host,
                Path("C:/FM2001"),
                platform_system="Windows",
                backend_factory=backend_factory,
            )

        self.assertIs(result, binding)
        load.assert_called_once_with(Path("C:/FM2001"))
        backend_factory.assert_called_once_with()
        install.assert_called_once_with(host, b"verified-bank", backend)


if __name__ == "__main__":
    unittest.main()
