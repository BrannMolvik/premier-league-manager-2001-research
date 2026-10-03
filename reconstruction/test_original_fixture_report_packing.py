import unittest

from original_fixture_report_packing import (
    pack_native_match_script, pack_native_participant_statistics,
    native_participant_skill_flags,
)


def native_record(size, fields):
    result = bytearray(size)
    for offset, value in fields.items():
        result[offset:offset + 4] = value.to_bytes(4, 'little')
    return bytes(result)


def expected_stream(chunks):
    # Independent integer concatenation oracle, not the byte-local writer.
    value, position = 0, 0
    for number, width in chunks:
        value |= (number & ((1 << width) - 1)) << position
        position += width
    return value.to_bytes((position + 7) // 8, 'little')


class NativeFixturePackingTests(unittest.TestCase):
    def test_source_skill_flags_threshold_mean_and_duplicate_selector(self):
        skills = [0] * 17
        for index, value in ((0, 200), (9, 199), (6, 201), (8, 199),
                             (10, 255), (7, 200), (4, 199)):
            skills[index] = value
        self.assertEqual(native_participant_skill_flags(tuple(skills)),
                         bytes((1, 0, 1, 0, 1, 1, 1, 0)))
        skills[9] = 200
        self.assertEqual(native_participant_skill_flags(tuple(skills))[1], 1)
        skills[7] = 199
        self.assertEqual(native_participant_skill_flags(tuple(skills))[5:7], b'\x00\x00')
        for invalid in (skills, (), (0,) * 16, (False,) * 17, (256,) * 17):
            with self.assertRaises(ValueError):
                native_participant_skill_flags(invalid)

    def test_participant_low_nibble_and_unaligned_next_record(self):
        first = bytearray(0x4C)
        first[0x30] = 0xA9
        first[0x35:0x3D] = bytes((1, 0, 1, 0, 1, 0, 1, 0))
        second = bytearray(0x4C)
        second[0x30] = 6
        second[0x35:0x3D] = bytes((0, 1, 0, 1, 0, 1, 0, 1))
        self.assertEqual(pack_native_participant_statistics((bytes(first),)),
                         bytes.fromhex('5905'))
        self.assertEqual(pack_native_participant_statistics((bytes(first), bytes(second))),
                         bytes.fromhex('5965aa'))

    def test_participant_count_capacity_and_no_destination_tail_invention(self):
        self.assertEqual(pack_native_participant_statistics(()), b'')
        self.assertEqual(len(pack_native_participant_statistics((bytes(0x4C),) * 18)), 27)
        with self.assertRaises(ValueError):
            pack_native_participant_statistics((bytes(0x4C),) * 19)

    def test_raw_bit_write_preserves_native_byte_spill_not_boolean_conversion(self):
        participant = bytearray(0x4C)
        participant[0x35] = 3
        self.assertEqual(pack_native_participant_statistics((bytes(participant),)), b'\x30\x00')
        participant[0x35] = 0xFF
        self.assertEqual(pack_native_participant_statistics((bytes(participant),)), b'\xf0\x00')

    def test_empty_script_has_ten_count_bits(self):
        self.assertEqual(pack_native_match_script(()), b'\x00\x00')

    def test_every_script_family_uses_native_prefix_and_payload_order(self):
        common = {0: 0x123, 4: 1, 8: 3, 0xC: 17, 0x10: 9,
                  0x14: 19, 0x18: 1, 0x1C: 0, 0x20: 1,
                  0x24: 5, 0x2C: 0x123456}
        payloads = {
            1: [(1, 1), (1, 1), (3, 5), (17, 5), (0, 1), (5, 3), (1, 1), (2, 2)],
            2: [(1, 1), (1, 1), (3, 5), (17, 5), (0, 1), (5, 3), (1, 1), (3, 2)],
            3: [(1, 1), (1, 1), (3, 5), (17, 5), (0, 1), (5, 3), (1, 1), (1, 2)],
            4: [(1, 1), (1, 1), (3, 5), (17, 5), (0, 1), (5, 3), (1, 1), (0, 2)],
            5: [(12, 4), (1, 1), (1, 1), (9, 5)],
            6: [(6, 3), (3, 2)],
            7: [(6, 3), (1, 2), (5, 2)],
            8: [(6, 3), (6, 3)],
            9: [(6, 3), (2, 3)],
            10: [(0, 4), (1, 1), (3, 5), (0x123456, 5)],
            11: [(4, 4), (1, 1), (4, 3), (0x123456, 5)],
            12: [(8, 4), (1, 1), (3, 5), (1, 1), (0x123456, 4)],
            13: [(2, 3), (0x56, 7), (0x34, 7), (0x12, 7)],
            14: [(8, 4), (1, 1), (3, 5), (0, 2), (0x123456, 4)],
            15: [(8, 4), (1, 1), (3, 5), (2, 2), (0x123456, 3), (5, 4)],
            16: [(6, 3), (0, 2)],
        }
        for kind, payload in payloads.items():
            with self.subTest(kind=kind):
                record = native_record(0x38, {**common, 0x28: kind})
                self.assertEqual(pack_native_match_script((record,)),
                                 expected_stream([(1, 10), (0x23, 8)] + payload))

    def test_chance_family_tags_decode_to_original_kind_not_ordinal(self):
        # Native 0x633D00 branch tree: 00 -> 4, 01 -> 3,
        # 10 -> 1, 11 -> 2 (LSB-first bit reader).
        for kind, golden in ((1, '0100040010'), (2, '0100040018'),
                             (3, '0100040008'), (4, '0100040000')):
            packed = pack_native_match_script((native_record(0x38, {0x28: kind}),))
            self.assertEqual(packed, bytes.fromhex(golden))
            tag = (int.from_bytes(packed, 'little') >> 35) & 3
            self.assertEqual((4, 3, 1, 2)[tag], kind)

    def test_incident_zero_branch_and_raw_flag_spill(self):
        record = native_record(0x38, {0x28: 5, 0x14: 19, 0x18: 1, 0x1C: 1})
        self.assertEqual(pack_native_match_script((record,)), expected_stream([
            (1, 10), (0, 8), (12, 4), (0, 1), (0, 1), (19, 5), (1, 1), (1, 1),
        ]))
        record = native_record(0x38, {0x28: 5, 0x20: 3})
        # The write is at bit 7 of this byte: its extra bit is discarded,
        # not carried into the following byte.
        self.assertEqual(pack_native_match_script((record,)), bytes.fromhex('0100b000'))

    def test_all_tactical_subcommands(self):
        payloads = (
            [(3, 2), (27, 3)], [(1, 2), (27, 3)], [(6, 3), (27, 2)],
            [(4, 3), (27, 5)], [(2, 3), (27, 4)],
            [(0, 3), (18, 5), (27, 5), (3, 2)],
        )
        for command, payload in enumerate(payloads):
            record = native_record(0x38, {0x28: 11, 8: command, 0xC: 18,
                                         0x2C: 27, 0x24: 3})
            with self.subTest(command=command):
                self.assertEqual(pack_native_match_script((record,)), expected_stream([
                    (1, 10), (0, 8), (4, 4), (0, 1), *payload,
                ]))

    def test_script_keeps_input_link_order_including_after_kind_nine(self):
        records = tuple(native_record(0x38, {0: time, 0x28: kind})
                        for time, kind in ((90, 9), (80, 6)))
        self.assertEqual(pack_native_match_script(records), expected_stream([
            (2, 10), (90, 8), (6, 3), (2, 3), (80, 8), (6, 3), (3, 2),
        ]))
        # The goals-array walk stops at kind 9; the script extraction does not.

    def test_invalid_inputs_never_become_partial_encoded_reports(self):
        for codec, size in ((pack_native_match_script, 0x38),
                            (pack_native_participant_statistics, 0x4C)):
            for bad in (None, [], (bytearray(size),), (bytes(size - 1),)):
                with self.subTest(codec=codec.__name__, bad=type(bad).__name__):
                    with self.assertRaises(ValueError):
                        codec(bad)
        for kind in (0, 17, 0xFFFFFFFF):
            with self.assertRaises(ValueError):
                pack_native_match_script((native_record(0x38, {0x28: kind}),))
        with self.assertRaises(ValueError):
            pack_native_match_script((native_record(0x38, {0x28: 11, 8: 6}),))
        with self.assertRaises(ValueError):
            pack_native_match_script((bytes(0x38),) * 1024)


if __name__ == '__main__':
    unittest.main()
