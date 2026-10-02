"""Tests for the source-disc Gate-14 audio candidate inventory."""
from types import SimpleNamespace
import unittest

from gate14_audio_source_inventory import (
    STARTUP_TGQ_PATHS,
    build_gate14_audio_source_inventory,
    render_inventory,
)


class Gate14AudioSourceInventoryTests(unittest.TestCase):
    def test_inventory_selects_banks_and_source_backed_startup_tgqs_only(self):
        files = (
            SimpleNamespace(path="DataInGame/audio/menu.bnk", size=10),
            SimpleNamespace(path="DataInGame/audio/MATCH.BNK", size=20),
            SimpleNamespace(path="FMV/easp.tgq", size=30),
            SimpleNamespace(path="FMV/premintro.tgq", size=40),
            SimpleNamespace(path="FMV/other.tgq", size=50),
            SimpleNamespace(path="FMV/Credits2.txt", size=60),
            SimpleNamespace(path="FM2001_Art/Generic/bground.444", size=70),
        )

        inventory = build_gate14_audio_source_inventory(files)

        self.assertEqual(len(inventory.bank_candidates), 2)
        self.assertEqual(
            [item.path for item in inventory.startup_tgqs],
            list(STARTUP_TGQ_PATHS),
        )
        self.assertEqual(
            [item.path for item in inventory.other_tgqs],
            ["FMV/other.tgq"],
        )
        self.assertTrue(
            all(item.source_kind == "bank_candidate" for item in inventory.bank_candidates)
        )

    def test_inventory_is_deterministic_and_case_insensitive_for_suffixes(self):
        inventory = build_gate14_audio_source_inventory((
            SimpleNamespace(path="z/SECOND.BNK", size=2),
            SimpleNamespace(path="A/first.bnk", size=1),
        ))
        self.assertEqual(
            [item.path for item in inventory.records],
            ["A/first.bnk", "z/SECOND.BNK"],
        )

    def test_duplicate_catalog_paths_fail_closed_case_insensitively(self):
        with self.assertRaisesRegex(ValueError, "duplicate source path"):
            build_gate14_audio_source_inventory((
                SimpleNamespace(path="Audio/Foo.bnk", size=1),
                SimpleNamespace(path="audio/foo.BNK", size=1),
            ))

    def test_receipt_keeps_bank_semantics_explicitly_unrecovered(self):
        inventory = build_gate14_audio_source_inventory((
            SimpleNamespace(path="Audio/Foo.bnk", size=1),
            SimpleNamespace(path="FMV/easp.tgq", size=2),
            SimpleNamespace(path="FMV/premintro.tgq", size=3),
        ))
        receipt = render_inventory(inventory, "/tmp/source.bin")
        self.assertEqual(receipt["bank_candidate_count"], 1)
        self.assertEqual(receipt["startup_tgq_count"], 2)
        self.assertFalse(
            receipt["semantic_boundary"]["bank_suffix_semantics_recovered"]
        )
        self.assertFalse(
            receipt["semantic_boundary"]["bank_entry_semantics_recovered"]
        )
        self.assertTrue(
            receipt["semantic_boundary"]["startup_tgq_ownership_recovered"]
        )


if __name__ == "__main__":
    unittest.main()
