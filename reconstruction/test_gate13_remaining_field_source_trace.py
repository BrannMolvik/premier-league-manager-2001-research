"""Candidate-only tests for unresolved Gate-13 field displacement tracing."""
from hashlib import sha256
from importlib.util import find_spec
import unittest

from gate13_button_source_trace import OriginalPE32
from gate13_remaining_field_source_trace import (
    REMAINING_GATE13_FIELDS,
    Gate13RemainingFieldTraceError,
    linear_memory_displacement_candidates,
    remaining_field_trace_report,
)
from test_gate13_button_source_trace import synthetic_pe


def field_fixture() -> OriginalPE32:
    fake = bytearray(synthetic_pe())
    # Keep a bounded NOP region so linear Capstone decode stays aligned.
    fake[0x200:0x280] = b"\x90" * 0x80

    # 0x401020: mov eax, dword ptr [ecx + 0x130]
    fake[0x220:0x226] = b"\x8B\x81\x30\x01\x00\x00"
    # 0x401030: mov dword ptr [edx + 0x13c], eax
    fake[0x230:0x236] = b"\x89\x82\x3C\x01\x00\x00"
    # 0x401040: cmp dword ptr [ebx + 0x140], 0
    fake[0x240:0x24A] = b"\x83\xBB\x40\x01\x00\x00\x00" + b"\x90" * 3
    # 0x401050: cmp byte ptr [eax + 0x76], 0
    fake[0x250:0x254] = b"\x80\x78\x76\x00"

    return OriginalPE32.parse(
        fake,
        expected_sha256=sha256(fake).hexdigest(),
    )


@unittest.skipUnless(find_spec("capstone"), "Capstone optional outside focused CI")
class RemainingFieldCandidateTests(unittest.TestCase):
    def test_field_seed_contract_is_explicit_and_unresolved(self):
        self.assertEqual(
            REMAINING_GATE13_FIELDS,
            (
                ("DBRClub legacy attendance-counter candidate", 0x130),
                ("DBRClub visiting-capacity candidate A", 0x13C),
                ("DBRClub visiting-capacity candidate B", 0x140),
                ("secondary/loan shirt selector candidate", 0x76),
            ),
        )

    def test_exact_displacement_hits_retain_register_context_without_semantics(self):
        hits = linear_memory_displacement_candidates(field_fixture())
        self.assertEqual(
            [
                (
                    item["candidate_instruction_va"],
                    item["candidate_displacement"],
                    item["base_register"],
                    item["candidate_operand_access"],
                )
                for item in hits
            ],
            [
                (0x401020, 0x130, "ecx", "read"),
                (0x401030, 0x13C, "edx", "write"),
                (0x401040, 0x140, "ebx", "read"),
                (0x401050, 0x76, "eax", "read"),
            ],
        )
        self.assertTrue(
            all(
                item["classification"]
                == "linear_disassembly_only_unconfirmed_memory_operand"
                for item in hits
            )
        )
        self.assertTrue(
            all(
                item["candidate_context_classification"]
                == "bounded_raw_bytes_only_not_a_cfg_or_function_boundary"
                for item in hits
            )
        )
        first = hits[0]
        self.assertEqual(first["candidate_instruction_size"], 6)
        self.assertEqual(first["candidate_context_start_va"], 0x401018)
        self.assertIn(first["candidate_bytes"], first["candidate_context_bytes"])

    def test_report_counts_candidates_but_does_not_promote_semantics(self):
        report = remaining_field_trace_report(field_fixture())
        self.assertEqual(report["candidate_count"], 4)
        self.assertEqual(report["candidate_context_radius_bytes"], 8)
        self.assertEqual(
            report["candidate_counts_by_displacement"],
            {"0x130": 1, "0x13C": 1, "0x140": 1, "0x76": 1},
        )
        self.assertFalse(report["source_semantics_recovered"])
        self.assertFalse(report["gate13_closed"])
        self.assertIn("Capstone operand metadata", report["evidence_limit"])
        self.assertIn("neither proves", report["evidence_limit"])

    def test_bounded_limit_and_invalid_inputs_fail_closed(self):
        hits = linear_memory_displacement_candidates(
            field_fixture(),
            max_candidates=2,
        )
        self.assertEqual(len(hits), 2)
        for bad in (0, True, 1.5):
            with self.subTest(max_candidates=bad):
                with self.assertRaises(Gate13RemainingFieldTraceError):
                    linear_memory_displacement_candidates(
                        field_fixture(),
                        max_candidates=bad,
                    )
        with self.assertRaises(Gate13RemainingFieldTraceError):
            linear_memory_displacement_candidates(
                field_fixture(),
                fields=(("", 0x130),),
            )
        with self.assertRaises(Gate13RemainingFieldTraceError):
            linear_memory_displacement_candidates(
                field_fixture(),
                fields=(("bad", -1),),
            )
        for bad_radius in (-1, True, 65):
            with self.subTest(context_radius=bad_radius):
                with self.assertRaises(Gate13RemainingFieldTraceError):
                    linear_memory_displacement_candidates(
                        field_fixture(),
                        context_radius=bad_radius,
                    )


if __name__ == "__main__":
    unittest.main()
