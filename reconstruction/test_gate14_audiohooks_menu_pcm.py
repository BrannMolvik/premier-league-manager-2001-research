"""Tests for source-backed numeric AudioHooks -> menus PCM composition."""
from dataclasses import replace
from hashlib import sha256
import struct
import unittest
from unittest import mock

from gate14_audio_bank_format import (
    BNK_TABLE_OFFSET,
    CANONICAL_FM2001_BANK_PROFILES,
)
from gate14_audiohooks_menu_pcm import (
    Gate14AudioHooksMenuPcmError,
    decode_audiohooks_menu_pcm,
)


def enc_patch(value: int) -> bytes:
    if value == 0:
        return b"\x00"
    size = max(1, (value.bit_length() + 7) // 8)
    return bytes([size]) + value.to_bytes(size, "big")


def synthetic_menus_bank() -> tuple[bytes, tuple[int, ...]]:
    # Preserve the native 23-slot menus table shape but materialize only slot 2.
    slot_count = 23
    header_size = 160
    samples = (1000, -1000, 1234)
    payload = struct.pack("<hhh", *samples)

    pt = bytearray(b"PT\x00\x00")
    pt += b"\xfd"
    pt += b"\x85" + enc_patch(len(samples))
    pt += b"\x88" + enc_patch(header_size)
    pt += b"\xff"

    table_end = BNK_TABLE_OFFSET + slot_count * 4
    pt_pos = table_end
    if pt_pos + len(pt) > header_size:
        raise AssertionError("synthetic menus metadata too large")

    out = bytearray(header_size)
    out[:4] = b"BNKl"
    out[4] = 2
    out[5] = 0
    out[6:8] = slot_count.to_bytes(2, "little")
    out[8:12] = header_size.to_bytes(4, "little")

    slot = 2
    entry = BNK_TABLE_OFFSET + slot * 4
    out[entry:entry + 4] = (pt_pos - entry).to_bytes(4, "little")
    out[pt_pos:pt_pos + len(pt)] = pt
    out += payload
    return bytes(out), samples


def synthetic_identity(raw: bytes) -> dict:
    return {
        "size_bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


class Gate14AudioHooksMenuPcmTests(unittest.TestCase):
    def test_numeric_event_routes_exact_slot_and_decodes_pcm(self):
        raw, samples = synthetic_menus_bank()
        with mock.patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": synthetic_identity(raw)},
        ):
            result = decode_audiohooks_menu_pcm(raw, 2, 0)

        self.assertEqual(result.event_id, 2)
        self.assertEqual(result.state_value, 0)
        self.assertEqual(result.sample_slot, 2)
        self.assertEqual(result.sample_rate, 22050)
        self.assertEqual(result.channels, 1)
        self.assertEqual(result.pcm_samples, samples)
        self.assertEqual(
            result.pcm_sha256,
            sha256(struct.pack("<hhh", *samples)).hexdigest(),
        )
        self.assertTrue(result.source_identity_verified)
        self.assertTrue(result.numeric_routing_recovered)
        self.assertTrue(result.sample_decode_recovered)
        self.assertFalse(result.semantic_event_binding_recovered)
        self.assertFalse(result.sample_meaning_recovered)
        self.assertFalse(result.host_audio_output_verified)

    def test_numeric_no_sound_route_stays_silent_without_semantic_promotion(self):
        raw, _ = synthetic_menus_bank()
        with mock.patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": synthetic_identity(raw)},
        ):
            result = decode_audiohooks_menu_pcm(raw, 7, 0)

        self.assertIsNone(result.sample_slot)
        self.assertIsNone(result.sample_rate)
        self.assertIsNone(result.channels)
        self.assertIsNone(result.pcm_samples)
        self.assertIsNone(result.pcm_sha256)
        self.assertFalse(result.semantic_event_binding_recovered)

    def test_rejects_noncanonical_bank_before_decoding(self):
        raw, _ = synthetic_menus_bank()
        with self.assertRaisesRegex(
            Gate14AudioHooksMenuPcmError,
            "canonical source identity",
        ):
            decode_audiohooks_menu_pcm(raw, 2, 0)

    def test_routed_slot_must_exist_in_verified_bank(self):
        raw, _ = synthetic_menus_bank()
        with mock.patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": synthetic_identity(raw)},
        ):
            with self.assertRaisesRegex(
                Gate14AudioHooksMenuPcmError,
                "missing menus.bnk sample slot",
            ):
                decode_audiohooks_menu_pcm(raw, 17, 0)

    def test_decoded_bridge_cannot_promote_meaning_or_audible_host_claims(self):
        raw, _ = synthetic_menus_bank()
        with mock.patch.dict(
            CANONICAL_FM2001_BANK_PROFILES,
            {"menus.bnk": synthetic_identity(raw)},
        ):
            result = decode_audiohooks_menu_pcm(raw, 2, 0)

        for field in (
            "semantic_event_binding_recovered",
            "sample_meaning_recovered",
            "host_audio_output_verified",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    Gate14AudioHooksMenuPcmError,
                    "cannot promote",
                ):
                    replace(result, **{field: True})


if __name__ == "__main__":
    unittest.main()
