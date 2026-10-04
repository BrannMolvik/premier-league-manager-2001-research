"""Contract tests for the real-Windows numeric menu-audio audible audit."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from gate14_audio_bank_format import CANONICAL_FM2001_BANK_PROFILES
from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch
from gate14_audiohooks_menu_playback import MenuPcmPlaybackSummary
from gate14_windows_menu_audio_audit import (
    AUDIBLE_CONFIRMATION_TOKEN,
    Gate14WindowsMenuAudioAuditError,
    _require_private_receipt,
    main as audit_main,
    run_windows_menu_audio_audit,
)


def decoded(*, slot: int | None = 6) -> DecodedMenuPcmDispatch:
    if slot is None:
        return DecodedMenuPcmDispatch(
            event_id=7,
            state_value=0,
            sample_slot=None,
            sample_rate=None,
            channels=None,
            pcm_samples=None,
            pcm_sha256=None,
        )
    return DecodedMenuPcmDispatch(
        event_id=17,
        state_value=0,
        sample_slot=slot,
        sample_rate=22050,
        channels=1,
        pcm_samples=(100, -100, 200),
        pcm_sha256="a" * 64,
    )


def delivery(*, slot: int = 6) -> MenuPcmPlaybackSummary:
    return MenuPcmPlaybackSummary(
        event_id=17,
        state_value=0,
        sample_slot=slot,
        backend_invoked=True,
        adapter_delivery_completed=True,
    )


class Gate14WindowsMenuAudioAuditTests(unittest.TestCase):
    def setUp(self):
        self.raw = b"synthetic-menus-bank"
        self.identity = {
            "size_bytes": len(self.raw),
            "sha256": sha256(self.raw).hexdigest(),
        }

    @patch("gate14_windows_menu_audio_audit.play_audiohooks_menu_pcm")
    @patch("gate14_windows_menu_audio_audit.decode_audiohooks_menu_pcm")
    def test_pass_requires_windows_delivery_and_exact_post_playback_yes(
        self,
        decode,
        play,
    ):
        item = decoded()
        decode.return_value = item
        play.return_value = delivery()
        backend = object()
        prompts = []

        def confirmer(prompt):
            prompts.append(prompt)
            return AUDIBLE_CONFIRMATION_TOKEN

        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            receipt = run_windows_menu_audio_audit(
                self.raw,
                event_id=17,
                state_value=0,
                backend=backend,
                confirmer=confirmer,
                platform_system="Windows",
                platform_text="Windows-11-test",
                python_version="3.12.test",
            )

        decode.assert_called_once_with(self.raw, 17, 0)
        play.assert_called_once_with(self.raw, 17, 0, backend)
        self.assertEqual(len(prompts), 1)
        self.assertIn("event_id=17", prompts[0])
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["schema_version"], 1)
        self.assertEqual(receipt["platform"], "Windows-11-test")
        self.assertEqual(receipt["python_version"], "3.12.test")
        self.assertEqual(receipt["source_bank"]["sha256"], self.identity["sha256"])
        self.assertEqual(receipt["numeric_route"], {
            "event_id": 17,
            "state_value": 0,
            "sample_slot": 6,
        })
        self.assertEqual(receipt["decoded_pcm"]["sample_rate"], 22050)
        self.assertEqual(receipt["decoded_pcm"]["channels"], 1)
        self.assertEqual(receipt["decoded_pcm"]["sample_count"], 3)
        self.assertEqual(receipt["decoded_pcm"]["sha256"], "a" * 64)
        self.assertTrue(receipt["adapter_delivery_completed"])
        self.assertTrue(receipt["human_audibility_confirmation"])
        self.assertTrue(receipt["audible_windows_verified"])
        self.assertFalse(receipt["semantic_event_binding_recovered"])
        self.assertFalse(receipt["sample_meaning_recovered"])
        self.assertFalse(receipt["modern_ui_event_equivalence_recovered"])
        self.assertFalse(receipt["login_menu_audio_integrated"])
        self.assertFalse(receipt["gate14_complete"])

    @patch("gate14_windows_menu_audio_audit.play_audiohooks_menu_pcm")
    @patch("gate14_windows_menu_audio_audit.decode_audiohooks_menu_pcm")
    def test_non_windows_and_noncanonical_source_fail_before_audible_claim(
        self,
        decode,
        play,
    ):
        with self.assertRaisesRegex(
            Gate14WindowsMenuAudioAuditError,
            "must run on Windows",
        ):
            run_windows_menu_audio_audit(
                self.raw,
                event_id=17,
                state_value=0,
                backend=object(),
                confirmer=lambda _: AUDIBLE_CONFIRMATION_TOKEN,
                platform_system="Linux",
            )
        decode.assert_not_called()
        play.assert_not_called()

        with self.assertRaisesRegex(
            Gate14WindowsMenuAudioAuditError,
            "canonical source identity",
        ):
            run_windows_menu_audio_audit(
                self.raw,
                event_id=17,
                state_value=0,
                backend=object(),
                confirmer=lambda _: AUDIBLE_CONFIRMATION_TOKEN,
                platform_system="Windows",
            )
        decode.assert_not_called()
        play.assert_not_called()

    @patch("gate14_windows_menu_audio_audit.play_audiohooks_menu_pcm")
    @patch("gate14_windows_menu_audio_audit.decode_audiohooks_menu_pcm")
    def test_silent_numeric_route_cannot_be_used_for_audibility_audit(
        self,
        decode,
        play,
    ):
        decode.return_value = decoded(slot=None)
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioAuditError,
                "real menus.bnk sample",
            ):
                run_windows_menu_audio_audit(
                    self.raw,
                    event_id=7,
                    state_value=0,
                    backend=object(),
                    confirmer=lambda _: AUDIBLE_CONFIRMATION_TOKEN,
                    platform_system="Windows",
                )
        play.assert_not_called()

    @patch("gate14_windows_menu_audio_audit.play_audiohooks_menu_pcm")
    @patch("gate14_windows_menu_audio_audit.decode_audiohooks_menu_pcm")
    def test_human_confirmation_fails_closed_after_successful_adapter_delivery(
        self,
        decode,
        play,
    ):
        decode.return_value = decoded()
        play.return_value = delivery()
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            for response in ("yes", "Y", "", "NO", "YES "):
                with self.subTest(response=response):
                    with self.assertRaisesRegex(
                        Gate14WindowsMenuAudioAuditError,
                        "not explicitly confirmed",
                    ):
                        run_windows_menu_audio_audit(
                            self.raw,
                            event_id=17,
                            state_value=0,
                            backend=object(),
                            confirmer=lambda _, value=response: value,
                            platform_system="Windows",
                        )

    @patch("gate14_windows_menu_audio_audit.play_audiohooks_menu_pcm")
    @patch("gate14_windows_menu_audio_audit.decode_audiohooks_menu_pcm")
    def test_delivery_summary_must_match_decoded_route(
        self,
        decode,
        play,
    ):
        decode.return_value = decoded(slot=6)
        play.return_value = delivery(slot=7)
        with patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": self.identity},
        ):
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioAuditError,
                "differs from decoded numeric route",
            ):
                run_windows_menu_audio_audit(
                    self.raw,
                    event_id=17,
                    state_value=0,
                    backend=object(),
                    confirmer=lambda _: AUDIBLE_CONFIRMATION_TOKEN,
                    platform_system="Windows",
                )

    def test_private_receipt_must_be_outside_git_and_new(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioAuditError,
                "outside Git",
            ):
                _require_private_receipt(
                    root / "receipt.json",
                    repository_root=root,
                )

            outside = Path(temp) / "private" / "receipt.json"
            checked = _require_private_receipt(
                outside,
                repository_root=root,
            )
            self.assertEqual(checked, outside.resolve())
            checked.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14WindowsMenuAudioAuditError,
                "do not overwrite",
            ):
                _require_private_receipt(
                    outside,
                    repository_root=root,
                )

    def test_cli_writes_only_returned_private_receipt(self):
        receipt = {
            "schema_version": 1,
            "passed": True,
            "audible_windows_verified": True,
            "semantic_event_binding_recovered": False,
            "login_menu_audio_integrated": False,
            "gate14_complete": False,
        }
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "menus.bnk"
            source.write_bytes(self.raw)
            output = Path(temp) / "private" / "audio.json"
            argv = [
                "gate14_windows_menu_audio_audit.py",
                str(source),
                "--event-id",
                "17",
                "--state-value",
                "0",
                "--output-receipt",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_windows_menu_audio_audit._require_windows",
                    return_value="Windows",
                ),
                patch(
                    "gate14_windows_menu_audio_audit.run_windows_menu_audio_audit",
                    return_value=receipt,
                ) as run,
            ):
                self.assertEqual(audit_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(emitted, receipt)
            run.assert_called_once()
            self.assertEqual(run.call_args.kwargs["event_id"], 17)
            self.assertEqual(run.call_args.kwargs["state_value"], 0)


if __name__ == "__main__":
    unittest.main()
