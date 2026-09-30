"""Synthetic i386 MSVC RTTI candidate discovery, never original UI fidelity."""
from hashlib import sha256
import os
from pathlib import Path
import struct
import unittest

from ea444_tables import CANONICAL_EXE_SHA256
from gate13_button_source_trace import OriginalPE32, OriginalPETraceError
from gate13_button_rtti_candidates import (
    BUTTON_TYPE_NAME, KNOWN_TEAMSELECT_TYPE_NAME,
    KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA, KNOWN_TEAMSELECT_VFTABLE_VA,
    button_rtti_candidate_report, calibrate_against_known_rtti,
    discover_msvc_button_vftables,
    require_known_positive_teamselect_calibration,
)


def make_pe() -> bytearray:
    """Three section miniature, with one plausible RTTI/CHD/vftable chain."""
    buf = bytearray(0x600)
    buf[:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)
    buf[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", buf, 0x84, 0x14C, 3)
    struct.pack_into("<H", buf, 0x80 + 20, 0xE0)
    opt = 0x80 + 24
    struct.pack_into("<H", buf, opt, 0x10B)
    struct.pack_into("<I", buf, opt + 28, 0x400000)
    sec = opt + 0xE0
    for index, (name, va, size, raw) in enumerate((
        (b".text", 0x1000, 0x80, 0x200),
        (b".rdata", 0x2000, 0x180, 0x300),
        (b".data", 0x3000, 0x40, 0x500),
    )):
        off = sec + 40 * index
        buf[off:off + len(name)] = name
        struct.pack_into("<IIII", buf, off + 8, size, va, size, raw)
    # TYPE_DESCRIPTOR: [p_type_info_vftable, spare, decorated_name+NUL].
    buf[0x318:0x318 + len(BUTTON_TYPE_NAME) + 1] = BUTTON_TYPE_NAME + b"\x00"
    struct.pack_into("<I", buf, 0x310, 0x403010)
    # COL: signature=0, subobject offset=0, cdOffset=0,
    #      pTypeDescriptor=0x402010, pClassHierarchy=0x4020C0
    struct.pack_into("<IIIII", buf, 0x380,
                     0, 0, 0, 0x402010, 0x4020C0)
    # ClassHierarchyDescriptor: signature=0, attributes=0,
    #    numBaseClasses=1, pBaseClassArray=0x4020D0.
    struct.pack_into("<IIII", buf, 0x3C0,
                     0, 0, 1, 0x4020D0)
    struct.pack_into("<I", buf, 0x3D0, 0x4020E0)
    # Vftable[-1] is pCOL; following slots point to .text.
    struct.pack_into("<IIII", buf, 0x400,
                     0x402080, 0x401020, 0x401030, 0)
    return buf


def as_pe(buf):
    raw = bytes(buf)
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class MSVCRTTILeadTests(unittest.TestCase):
    def test_decorated_name_is_grounded_in_known_original_rtti_family(self):
        self.assertEqual(BUTTON_TYPE_NAME, b".?AVButton@ease_2001@@")
        with self.assertRaisesRegex(OriginalPETraceError, "expected original"):
            OriginalPE32.parse(bytes(make_pe()))

    def test_exact_synthetic_msvc_rtti_chain_to_bounded_code_slots(self):
        pe = as_pe(make_pe())
        hits = discover_msvc_button_vftables(pe)
        self.assertEqual(len(hits), 1)
        hit = hits[0]
        self.assertEqual(
            (hit.type_descriptor_va, hit.col_va,
             hit.class_hierarchy_descriptor_va, hit.vftable_va),
            (0x402010, 0x402080, 0x4020C0, 0x402104),
        )
        self.assertEqual(
            [item["target_va_unconfirmed"] for item in hit.candidate_code_slots],
            [0x401020, 0x401030],
        )
        self.assertIn("candidate", hit.classification)
        report = button_rtti_candidate_report(pe)
        self.assertEqual(report["candidate_count"], 1)
        self.assertIn("manual", report["evidence_limit"].lower())
        self.assertNotIn("verified_vftables", report)
        self.assertEqual(len(discover_msvc_button_vftables(pe, max_slots=1)[0].candidate_code_slots), 1)

    def test_same_rtti_parser_recovers_independently_pinned_reference_class(self):
        self.assertEqual(KNOWN_TEAMSELECT_TYPE_NAME, b".?AVPMain@TeamSelect@@")
        self.assertEqual(KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA, 0x81EC10)
        self.assertEqual(KNOWN_TEAMSELECT_VFTABLE_VA, 0x7C7650)
        # A separate known-reference chain coexists with synthetic Button;
        # miniature fixture VAs are test-only, never original executable VA.
        data = make_pe()
        name = KNOWN_TEAMSELECT_TYPE_NAME + b"\x00"
        data[0x348:0x348 + len(name)] = name
        struct.pack_into("<IIIII", data, 0x3A0,
                         0, 0, 0, 0x402040, 0x4020C0)
        struct.pack_into("<III", data, 0x420,
                         0x4020A0, 0x401040, 0)
        pe = as_pe(data)
        synthetic_calibration = calibrate_against_known_rtti(
            pe,
            expected_type_descriptor_va=0x402040,
            expected_vftable_va=0x402124,
        )
        self.assertTrue(
            synthetic_calibration["expected_pair_recovered_by_same_pattern_decoder"]
        )
        self.assertEqual(synthetic_calibration["candidate_count"], 1)
        report = button_rtti_candidate_report(pe)
        self.assertEqual(report["candidate_count"], 1)
        self.assertFalse(
            report["known_original_teamselect_rtti_calibration"]
                  ["expected_pair_recovered_by_same_pattern_decoder"]
        )
        wrong_descriptor = calibrate_against_known_rtti(
            pe, expected_type_descriptor_va=0x402080,
            expected_vftable_va=0x402124,
        )
        wrong_vftable = calibrate_against_known_rtti(
            pe, expected_type_descriptor_va=0x402040,
            expected_vftable_va=0x402104,
        )
        self.assertFalse(wrong_descriptor["expected_pair_recovered_by_same_pattern_decoder"])
        self.assertFalse(wrong_vftable["expected_pair_recovered_by_same_pattern_decoder"])
        # Tampering the known-positive CHD prevents a false calibration.
        struct.pack_into("<I", data, 0x3C8, 0)
        self.assertFalse(
            calibrate_against_known_rtti(
                as_pe(data),
                expected_type_descriptor_va=0x402040,
                expected_vftable_va=0x402124,
            )["expected_pair_recovered_by_same_pattern_decoder"]
        )

    def test_known_original_canary_guard_rejects_missing_wrong_and_false_evidence(self):
        baseline = {
            "known_original_teamselect_rtti_calibration": {
                "known_reference_decorated_name": KNOWN_TEAMSELECT_TYPE_NAME.decode("ascii"),
                "previously_proven_type_descriptor_va": KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA,
                "previously_proven_vftable_va": KNOWN_TEAMSELECT_VFTABLE_VA,
                "expected_pair_recovered_by_same_pattern_decoder": True,
            },
            "candidates_not_validated_vtables": [],
        }
        self.assertIsNone(require_known_positive_teamselect_calibration(baseline))
        cases = [
            {},
            {"known_original_teamselect_rtti_calibration": None},
            {"known_original_teamselect_rtti_calibration": {}},
        ]
        for k, v in (
            ("known_reference_decorated_name", "invented class"),
            ("previously_proven_type_descriptor_va", 0x402010),
            ("previously_proven_vftable_va", 0x402104),
            ("expected_pair_recovered_by_same_pattern_decoder", False),
            ("expected_pair_recovered_by_same_pattern_decoder", 1),
        ):
            broken = dict(baseline["known_original_teamselect_rtti_calibration"])
            broken[k] = v
            cases.append({"known_original_teamselect_rtti_calibration": broken})
        for invalid in cases:
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(OriginalPETraceError, "did not recover"):
                    require_known_positive_teamselect_calibration(invalid)

    def test_rejects_broken_name_locator_hierarchy_vftable_and_alignment(self):
        for label, offset, value in (
            ("wrong class literal", 0x31B, b"z"),
            ("not signature zero", 0x380, struct.pack("<I", 1)),
            ("bad TD pointer", 0x38C, struct.pack("<I", 0x402050)),
            ("unmapped CHD pointer", 0x390, struct.pack("<I", 0x499999)),
            ("invalid hierarchy base count", 0x3C8, struct.pack("<I", 0)),
            ("unmapped hierarchy base array", 0x3CC, struct.pack("<I", 0x499999)),
            ("not a COL pointer", 0x400, struct.pack("<I", 0x402040)),
            ("no code pointer slot", 0x404, struct.pack("<I", 0x402120)),
        ):
            with self.subTest(case=label):
                data = make_pe()
                data[offset:offset + len(value)] = value
                hits = discover_msvc_button_vftables(as_pe(data))
                # A table whose first slot is not code is rejected, even
                # if some later bytes happen to resemble executable pointers.
                self.assertEqual(hits, ())
        for name in (b"", b"unqualified", b"\x00.?AVButton@@"):
            with self.subTest(decorated=name):
                with self.assertRaisesRegex(OriginalPETraceError, "decorated"):
                    discover_msvc_button_vftables(as_pe(make_pe()), decorated_name=name)

    def test_multi_subobject_locator_and_caps_do_not_invent_role(self):
        data = make_pe()
        # A second plausible COL for the same type with different subobject
        # offset proves candidates remain distinct instead of resolving roles.
        struct.pack_into("<IIIII", data, 0x3A0,
                         0, 4, 0, 0x402010, 0x4020C0)
        struct.pack_into("<III", data, 0x414, 0x4020A0, 0x401020, 0)
        hits = discover_msvc_button_vftables(as_pe(data))
        self.assertEqual(
            [(hit.col_offset, hit.vftable_va) for hit in hits],
            [(0, 0x402104), (4, 0x402118)],
        )
        self.assertEqual(len(discover_msvc_button_vftables(as_pe(data), max_vftables=1)), 1)
        for kwargs in (
            {"max_vftables": 0}, {"max_vftables": 65},
            {"max_slots": 0}, {"max_slots": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(OriginalPETraceError):
                    discover_msvc_button_vftables(as_pe(data), **kwargs)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE"),
        "Licensed original executable intentionally not bundled in hosted CI",
    )
    def test_opt_in_reports_unconfirmed_original_rtti_leads(self):
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        self.assertEqual(pe.sha256, CANONICAL_EXE_SHA256)
        report = button_rtti_candidate_report(pe)
        self.assertEqual(report["source_sha256"], CANONICAL_EXE_SHA256)
        self.assertIn("manual", report["evidence_limit"].lower())
        calibration = report["known_original_teamselect_rtti_calibration"]
        self.assertEqual(calibration["previously_proven_type_descriptor_va"],
                         KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA)
        self.assertEqual(calibration["previously_proven_vftable_va"],
                         KNOWN_TEAMSELECT_VFTABLE_VA)
        # This must genuinely recover the previously proven original
        # reference pair before any new Button candidate is promoted.
        self.assertTrue(
            calibration["expected_pair_recovered_by_same_pattern_decoder"]
        )
        for candidate in report["candidates_not_validated_vtables"]:
            self.assertTrue(candidate["candidate_code_slots"])
            self.assertIn("candidate", candidate["classification"])


if __name__ == "__main__":
    unittest.main()
