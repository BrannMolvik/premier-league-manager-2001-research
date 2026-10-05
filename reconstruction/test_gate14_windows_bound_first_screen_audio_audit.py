"""Tests for the real-Windows production-host first-screen audio audit."""
from hashlib import sha256
import inspect
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from front_end_state import FrontEndScreen
from gate14_audiohooks_menu_playback import (
    Gate14MenuPcmPlaybackError,
    MenuPcmPlaybackSummary,
)
from gate14_first_screen_audio_binding import install_first_screen_press_audio
from gate14_windows_menu_pcm_backend import WindowsMemoryWaveMenuPcmBackend
import gate14_windows_bound_first_screen_audio_audit as audit
import original_game_host


FAKE_BANK = b"canonical-test-menus-bank"


class FakeRoot:
    def __init__(self):
        self.destroyed = False
        self.after_calls = 0

    def after(self, delay, callback):
        self.after_calls += 1
        self.last_delay = delay
        callback()

    def destroy(self):
        self.destroyed = True


class FakeCanvas:
    def __init__(self):
        self.bindings = {}
        self.generated = []

    def bind(self, sequence, callback):
        self.bindings[sequence] = callback

    def event_generate(self, sequence, **kwargs):
        self.generated.append((sequence, kwargs))
        return self.bindings[sequence](SimpleNamespace(**kwargs))


class FakeHost:
    def __init__(self):
        self.root = FakeRoot()
        self.canvas = FakeCanvas()
        self.presenter = SimpleNamespace(
            session=SimpleNamespace(
                navigation=SimpleNamespace(screen=FrontEndScreen.START_MENU)
            )
        )
        self.click_count = 0

    def on_click(self, event):
        self.click_count += 1
        self.presenter.session.navigation.screen = FrontEndScreen.TEAM_SELECT
        return event


def _summary():
    return MenuPcmPlaybackSummary(
        event_id=10,
        state_value=0,
        sample_slot=2,
        backend_invoked=True,
        adapter_delivery_completed=True,
    )


def _profile_patch():
    return patch.dict(
        audit.CANONICAL_FM2001_BANK_PROFILES,
        {
            "menus.bnk": {
                "size_bytes": len(FAKE_BANK),
                "sha256": sha256(FAKE_BANK).hexdigest(),
            }
        },
        clear=False,
    )


class Gate14WindowsBoundFirstScreenAudioAuditTests(unittest.TestCase):
    def test_production_runner_audit_requires_real_bound_tk_press_and_human_hearing(self):
        observed = {}

        def fake_runner(game_dir, *, source_root=None, host_ready_callback=None, **kwargs):
            host = FakeHost()
            backend = WindowsMemoryWaveMenuPcmBackend(
                player=lambda data, flags: None,
                memory_flag=4,
            )
            binding = install_first_screen_press_audio(host, FAKE_BANK, backend)
            observed["host"] = host
            observed["binding"] = binding
            observed["game_dir"] = Path(game_dir)
            observed["source_root"] = source_root
            host_ready_callback(host, binding)

        with (
            patch.object(audit, "run_original_game_ui", fake_runner),
            patch(
                "gate14_first_screen_audio_binding."
                "play_verified_first_screen_action_press",
                return_value=_summary(),
            ),
            _profile_patch(),
        ):
            receipt = audit.run_windows_bound_first_screen_audio_audit(
                r"C:\\Games\\FM2001",
                source_root=Path("source-root"),
                confirmer=lambda prompt: audit.AUDIBLE_CONFIRMATION_TOKEN,
                platform_system="Windows",
                platform_release="11",
                platform_version="10.0.26100",
                github_actions="",
                windows_product_type=1,
            )

        host = observed["host"]
        binding = observed["binding"]
        self.assertTrue(host.root.destroyed)
        self.assertEqual(host.root.after_calls, 1)
        self.assertEqual(host.click_count, 1)
        self.assertEqual(len(host.canvas.generated), 1)
        sequence, event = host.canvas.generated[0]
        self.assertEqual(sequence, "<Button-1>")
        self.assertEqual(receipt["source_screen_before"], "START_MENU")
        self.assertEqual(receipt["source_screen_after"], "TEAM_SELECT")
        self.assertEqual(receipt["source_action_event"], 2)
        self.assertEqual(receipt["binding_class"], type(binding).__name__)
        self.assertEqual(receipt["audio_attempt_count"], 1)
        self.assertEqual(receipt["audio_success_count"], 1)
        self.assertEqual(receipt["numeric_event_id"], 10)
        self.assertEqual(receipt["state_value"], 0)
        self.assertEqual(receipt["sample_slot"], 2)
        self.assertTrue(receipt["adapter_delivery_completed"])
        self.assertTrue(receipt["human_audibility_confirmation"])
        self.assertTrue(receipt["bound_application_press_audio_verified"])
        self.assertTrue(receipt["audible_windows_verified"])
        self.assertFalse(receipt["broad_audio_event_binding_recovered"])
        self.assertFalse(receipt["sample_meaning_recovered"])
        self.assertFalse(receipt["hover_audio_integrated"])
        self.assertFalse(receipt["login_menu_audio_integrated"])
        self.assertFalse(receipt["gate14_complete"])

    def test_audio_failure_still_delegates_but_acceptance_fails_closed(self):
        observed = {}

        def fake_runner(game_dir, *, source_root=None, host_ready_callback=None, **kwargs):
            host = FakeHost()
            backend = WindowsMemoryWaveMenuPcmBackend(
                player=lambda data, flags: None,
                memory_flag=4,
            )
            binding = install_first_screen_press_audio(host, FAKE_BANK, backend)
            observed["host"] = host
            host_ready_callback(host, binding)

        with (
            patch.object(audit, "run_original_game_ui", fake_runner),
            patch(
                "gate14_first_screen_audio_binding."
                "play_verified_first_screen_action_press",
                side_effect=Gate14MenuPcmPlaybackError("test delivery failure"),
            ),
            _profile_patch(),
        ):
            with self.assertRaisesRegex(
                audit.Gate14WindowsBoundFirstScreenAudioAuditError,
                "exactly one successful audio attempt",
            ):
                audit.run_windows_bound_first_screen_audio_audit(
                    r"C:\\Games\\FM2001",
                    confirmer=lambda prompt: audit.AUDIBLE_CONFIRMATION_TOKEN,
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=1,
                )

        self.assertEqual(observed["host"].click_count, 1)
        self.assertEqual(
            observed["host"].presenter.session.navigation.screen,
            FrontEndScreen.TEAM_SELECT,
        )

    def test_human_rejection_fails_closed_after_exact_adapter_delivery(self):
        def fake_runner(game_dir, *, source_root=None, host_ready_callback=None, **kwargs):
            host = FakeHost()
            binding = install_first_screen_press_audio(
                host,
                FAKE_BANK,
                WindowsMemoryWaveMenuPcmBackend(
                    player=lambda data, flags: None,
                    memory_flag=4,
                ),
            )
            host_ready_callback(host, binding)

        with (
            patch.object(audit, "run_original_game_ui", fake_runner),
            patch(
                "gate14_first_screen_audio_binding."
                "play_verified_first_screen_action_press",
                return_value=_summary(),
            ),
            _profile_patch(),
        ):
            with self.assertRaisesRegex(
                audit.Gate14WindowsBoundFirstScreenAudioAuditError,
                "not explicitly confirmed audible",
            ):
                audit.run_windows_bound_first_screen_audio_audit(
                    r"C:\\Games\\FM2001",
                    confirmer=lambda prompt: "NO",
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=1,
                )

    def test_external_windows_guard_rejects_non_windows_actions_server_and_old_build(self):
        common = dict(
            platform_release="11",
            platform_version="10.0.26100",
            github_actions="",
            windows_product_type=1,
        )
        with self.assertRaisesRegex(
            audit.Gate14WindowsBoundFirstScreenAudioAuditError,
            "must run on Windows 11",
        ):
            audit._require_external_windows_11(
                platform_system="Linux",
                **common,
            )
        with self.assertRaisesRegex(
            audit.Gate14WindowsBoundFirstScreenAudioAuditError,
            "GitHub Actions",
        ):
            audit._require_external_windows_11(
                platform_system="Windows",
                **{**common, "github_actions": "true"},
            )
        with self.assertRaisesRegex(
            audit.Gate14WindowsBoundFirstScreenAudioAuditError,
            "client workstation",
        ):
            audit._require_external_windows_11(
                platform_system="Windows",
                **{**common, "windows_product_type": 3},
            )
        with self.assertRaisesRegex(
            audit.Gate14WindowsBoundFirstScreenAudioAuditError,
            "build 22000",
        ):
            audit._require_external_windows_11(
                platform_system="Windows",
                platform_release="10",
                platform_version="10.0.19045",
                github_actions="",
                windows_product_type=1,
            )

    def test_receipt_must_be_outside_repo_and_non_overwriting(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(
                audit.Gate14WindowsBoundFirstScreenAudioAuditError,
                "outside Git",
            ):
                audit._require_private_receipt(
                    root / "receipt.json",
                    repository_root=root,
                )

            outside = Path(td) / "private" / "receipt.json"
            target = audit._require_private_receipt(
                outside,
                repository_root=root,
            )
            self.assertEqual(target, outside.resolve())
            target.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(
                audit.Gate14WindowsBoundFirstScreenAudioAuditError,
                "do not overwrite",
            ):
                audit._require_private_receipt(
                    target,
                    repository_root=root,
                )

    def test_production_host_observer_is_after_audio_install_and_before_mainloop(self):
        source = inspect.getsource(original_game_host.run_original_game_ui)
        install = source.index(
            "audio_binding = install_live_first_screen_audio(host, game_dir)"
        )
        observe = source.index("host_ready_callback(host, audio_binding)")
        loop = source.index("root.mainloop()")
        self.assertLess(install, observe)
        self.assertLess(observe, loop)
        self.assertIn("host_ready_callback=None", source)
        self.assertIn(
            'raise OriginalGameHostError("host_ready_callback must be callable")',
            source,
        )


if __name__ == "__main__":
    unittest.main()
