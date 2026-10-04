"""Tests for the exact FM2001 BNKl v2 parser/decoder."""
import struct
import unittest

from gate14_audio_bank_format import (
    BNK_TABLE_OFFSET,
    DEFAULT_PC_SAMPLE_RATE,
    EA_XA_FRAME_BYTES,
    FM2001BnkSample,
    Gate14BnkFormatError,
    decode_fm2001_bnk_sample,
    parse_fm2001_bnk,
    pcm16le_bytes,
)


def patch(value: int) -> bytes:
    if value == 0:
        return b"\x00"
    size = max(1, (value.bit_length() + 7) // 8)
    return bytes([size]) + value.to_bytes(size, "big")


def pt(*, samples: int, data_offset: int, codec: int | None, loop=None) -> bytes:
    out = bytearray(b"PT\x00\x00")
    out += b"\xfd"
    out += b"\x85" + patch(samples)
    if codec is not None:
        out += b"\x83" + patch(codec)
    if loop is not None:
        start, end_exclusive = loop
        out += b"\x86" + patch(start)
        out += b"\x87" + patch(end_exclusive - 1)
    out += b"\x88" + patch(data_offset)
    out += b"\x8a" + patch(0)
    out += b"\xff"
    return bytes(out)


def synthetic_bank():
    # Three slots: PCM, EA-XA, dummy. Metadata is padded to payload offset 96.
    slot_count = 3
    header_size = 96
    pcm_samples = (1000, -1000, 32767)
    pcm = struct.pack("<hhh", *pcm_samples)
    pcm_offset = header_size
    xa_offset = pcm_offset + len(pcm) + 2  # valid 2-byte alignment padding
    xa = bytes([0x00]) + bytes(EA_XA_FRAME_BYTES - 1)  # one silent frame

    p0 = pt(samples=len(pcm_samples), data_offset=pcm_offset, codec=None)
    p1 = pt(samples=28, data_offset=xa_offset, codec=7, loop=(2, 20))

    table_end = BNK_TABLE_OFFSET + slot_count * 4
    p0_pos = table_end
    p1_pos = p0_pos + len(p0)
    if p1_pos + len(p1) > header_size:
        raise AssertionError("synthetic metadata too large")

    out = bytearray(header_size)
    out[:4] = b"BNKl"
    out[4] = 2
    out[5] = 0
    out[6:8] = slot_count.to_bytes(2, "little")
    out[8:12] = header_size.to_bytes(4, "little")
    for slot, target in ((0, p0_pos), (1, p1_pos)):
        entry = BNK_TABLE_OFFSET + slot * 4
        out[entry:entry + 4] = (target - entry).to_bytes(4, "little")
    # slot 2 stays zero/dummy
    out[p0_pos:p0_pos + len(p0)] = p0
    out[p1_pos:p1_pos + len(p1)] = p1
    out += pcm
    out += b"\x00\x00"
    out += xa
    out += b"\x00\x00\x00"  # valid final alignment padding
    return bytes(out), pcm_samples


class Gate14AudioBankFormatTests(unittest.TestCase):
    def test_parses_relative_pt_table_defaults_alias_safe_spans(self):
        raw, pcm_samples = synthetic_bank()
        bank = parse_fm2001_bnk(raw)

        self.assertEqual(bank.version, 2)
        self.assertEqual(bank.slot_count, 3)
        self.assertEqual(bank.header_size, 96)
        self.assertEqual(bank.real_sound_count, 2)
        self.assertEqual(bank.dummy_slots, (2,))

        pcm, xa = bank.samples
        self.assertEqual(pcm.slot_index, 0)
        self.assertEqual(pcm.codec, "pcm16le")
        self.assertEqual(pcm.codec1_value, 0)
        self.assertEqual(pcm.sample_rate, DEFAULT_PC_SAMPLE_RATE)
        self.assertEqual(pcm.channels, 1)
        self.assertEqual(pcm.encoded_size, len(pcm_samples) * 2)
        self.assertEqual(pcm.alignment_padding, 2)

        self.assertEqual(xa.slot_index, 1)
        self.assertEqual(xa.codec, "ea_xa_v1")
        self.assertEqual(xa.codec1_value, 7)
        self.assertEqual(xa.sample_count, 28)
        self.assertEqual(xa.encoded_size, 15)
        self.assertEqual(xa.alignment_padding, 3)
        self.assertEqual((xa.loop_start, xa.loop_end), (2, 20))

    def test_decodes_pcm_and_ea_xa_to_exact_sample_counts(self):
        raw, pcm_samples = synthetic_bank()
        bank = parse_fm2001_bnk(raw)
        pcm, xa = bank.samples

        self.assertEqual(decode_fm2001_bnk_sample(raw, pcm), pcm_samples)
        self.assertEqual(
            decode_fm2001_bnk_sample(raw, xa),
            (0,) * 28,
        )
        self.assertEqual(
            pcm16le_bytes(pcm_samples),
            struct.pack("<hhh", *pcm_samples),
        )

    def test_ea_xa_predictor_path_is_deterministic(self):
        # filter=1, shift=0 => predictor 240/0; 14 packed 0x11 bytes.
        frame = bytes([0x10]) + bytes([0x11] * 14)
        # Lock the first few decoder outputs, not only length/silence behavior.
        sample = FM2001BnkSample(
            slot_index=0,
            pt_offset=12,
            data_offset=64,
            sample_count=28,
            sample_rate=22050,
            channels=1,
            codec="ea_xa_v1",
            codec1_value=7,
            encoded_size=15,
            available_span=15,
            alignment_padding=0,
        )
        raw = bytes(64) + frame
        decoded = decode_fm2001_bnk_sample(raw, sample)
        self.assertEqual(len(decoded), 28)
        self.assertEqual(decoded[:6], (16, 31, 45, 58, 70, 81))

    def test_rejects_bad_signature_version_bounds_and_truncated_payload(self):
        raw, _ = synthetic_bank()
        with self.assertRaisesRegex(Gate14BnkFormatError, "not a little-endian"):
            parse_fm2001_bnk(b"BAD!" + raw[4:])
        bad_version = bytearray(raw)
        bad_version[4] = 4
        with self.assertRaisesRegex(Gate14BnkFormatError, "unsupported BNK"):
            parse_fm2001_bnk(bytes(bad_version))

        bank = parse_fm2001_bnk(raw)
        xa = bank.samples[1]
        with self.assertRaisesRegex(Gate14BnkFormatError, "exceeds bank"):
            decode_fm2001_bnk_sample(raw[:xa.data_offset + 5], xa)


if __name__ == "__main__":
    unittest.main()
