"""Tests for the fail-closed Gate-15 fidelity ledger coverage audit."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from gate15_fidelity_ledger import (
    Gate15FidelityLedgerError,
    audit_gate15_fidelity,
    audit_repository_gate15,
    load_fidelity_ledger,
    parse_active_fidelity_gaps,
    roadmap_gate_complete,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
GAPS_PATH = REPO_ROOT / "research" / "FIDELITY_GAPS.md"
LEDGER_PATH = REPO_ROOT / "research" / "GATE15_FIDELITY_ACCEPTANCE_LEDGER.json"


def _canonical_markdown() -> str:
    return GAPS_PATH.read_text(encoding="utf-8")


def _canonical_payload() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def _synthetic_markdown() -> str:
    return """# Fidelity Gaps

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| First gap | bounded behavior | exact behavior unresolved | 15 |
| Second gap | bounded behavior | exact behavior unresolved | 15 or later fidelity work |

## Resolved or superseded gaps
"""


def _synthetic_final_payload(*, declared: bool = True) -> dict:
    return {
        "schema_version": 1,
        "source_path": "research/FIDELITY_GAPS.md",
        "gate15_declared_complete": declared,
        "items": [
            {
                "gap": "First gap",
                "planned_gate": "15",
                "owner_gate": 15,
                "status": "fixed",
                "fallback_described_as_original": False,
                "release_limitation_required_if_accepted": False,
            },
            {
                "gap": "Second gap",
                "planned_gate": "15 or later fidelity work",
                "owner_gate": 15,
                "status": "accepted_documented",
                "fallback_described_as_original": False,
                "release_limitation_required_if_accepted": True,
            },
        ],
    }


class Gate15FidelityLedgerTests(unittest.TestCase):
    def test_canonical_ledger_covers_every_active_gap_exactly_once(self):
        audit = audit_repository_gate15(REPO_ROOT)

        self.assertEqual(audit.active_gap_count, 11)
        self.assertEqual(audit.ledger_item_count, 11)
        self.assertEqual(audit.missing_from_ledger, ())
        self.assertEqual(audit.unexpected_in_ledger, ())
        self.assertEqual(audit.planned_gate_mismatches, ())
        self.assertTrue(audit.all_fallback_claims_fail_closed)
        self.assertFalse(audit.all_gate15_items_final)
        self.assertFalse(audit.gate15_ready)
        self.assertEqual(
            audit.gate14_prerequisite_items,
            ("FastView/3D and original audio/match presentation",),
        )
        self.assertIn(("prerequisite_gate_14", 1), audit.status_counts)

    def test_repository_audit_derives_gate14_open_from_roadmap(self):
        audit = audit_repository_gate15(REPO_ROOT)

        self.assertFalse(audit.gate14_complete)
        self.assertFalse(audit.gate15_ready)

    def test_roadmap_gate_complete_requires_all_gate14_criteria_checked(self):
        open_roadmap = """# Roadmap
## Gate 14 - Audio
- [x] One
- [ ] Two
## Gate 15 - Fidelity
- [ ] Three
"""
        closed_roadmap = open_roadmap.replace("- [ ] Two", "- [x] Two")

        self.assertFalse(roadmap_gate_complete(open_roadmap, 14))
        self.assertTrue(roadmap_gate_complete(closed_roadmap, 14))

    def test_roadmap_gate_complete_rejects_missing_or_empty_gate(self):
        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "missing Gate 14",
        ):
            roadmap_gate_complete("## Gate 13 - Old\n- [x] Done\n", 14)

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "has no completion criteria",
        ):
            roadmap_gate_complete("## Gate 14 - Audio\nNo checkboxes yet\n", 14)

    def test_gate14_completion_alone_cannot_accept_pending_gate15_items(self):
        audit = audit_gate15_fidelity(
            _canonical_markdown(),
            _canonical_payload(),
            gate14_complete=True,
        )

        self.assertTrue(audit.gate14_complete)
        self.assertFalse(audit.all_gate15_items_final)
        self.assertTrue(audit.gate14_prerequisite_items)
        self.assertFalse(audit.gate15_ready)

    def test_missing_ledger_item_is_reported(self):
        payload = _canonical_payload()
        removed = payload["items"].pop()

        audit = audit_gate15_fidelity(
            _canonical_markdown(),
            payload,
            gate14_complete=False,
        )

        self.assertEqual(audit.missing_from_ledger, (removed["gap"],))
        self.assertFalse(audit.gate15_ready)

    def test_unexpected_ledger_item_is_reported(self):
        payload = _canonical_payload()
        extra = copy.deepcopy(payload["items"][0])
        extra["gap"] = "Not an active fidelity gap"
        payload["items"].append(extra)

        audit = audit_gate15_fidelity(
            _canonical_markdown(),
            payload,
            gate14_complete=False,
        )

        self.assertEqual(
            audit.unexpected_in_ledger,
            ("Not an active fidelity gap",),
        )
        self.assertFalse(audit.gate15_ready)

    def test_planned_gate_drift_is_reported(self):
        payload = _canonical_payload()
        payload["items"][0]["planned_gate"] = "99"

        audit = audit_gate15_fidelity(
            _canonical_markdown(),
            payload,
            gate14_complete=False,
        )

        self.assertEqual(
            audit.planned_gate_mismatches,
            ("Secondary startup exact tie permutation and bucket shape",),
        )
        self.assertFalse(audit.gate15_ready)

    def test_duplicate_ledger_gap_is_rejected(self):
        payload = _canonical_payload()
        payload["items"].append(copy.deepcopy(payload["items"][0]))

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "duplicate gaps",
        ):
            load_fidelity_ledger(payload)

    def test_fallback_cannot_be_described_as_original(self):
        payload = _canonical_payload()
        payload["items"][0]["fallback_described_as_original"] = True

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "fallback-as-original",
        ):
            load_fidelity_ledger(payload)

    def test_accepted_gap_must_be_carried_to_release_limitations(self):
        payload = _canonical_payload()
        payload["items"][0]["status"] = "accepted_documented"
        payload["items"][0]["release_limitation_required_if_accepted"] = False

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "carried to release limitations",
        ):
            load_fidelity_ledger(payload)

    def test_gate14_owned_gap_cannot_be_relabelled_as_gate15_acceptance(self):
        payload = _canonical_payload()
        item = payload["items"][-1]
        self.assertEqual(item["owner_gate"], 14)
        item["status"] = "accepted_documented"
        item["release_limitation_required_if_accepted"] = True

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "Gate-14-owned gap",
        ):
            load_fidelity_ledger(payload)

    def test_declared_completion_fails_closed_while_any_item_is_pending(self):
        payload = _canonical_payload()
        payload["gate15_declared_complete"] = True

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "cannot be declared complete",
        ):
            audit_gate15_fidelity(
                _canonical_markdown(),
                payload,
                gate14_complete=False,
            )

    def test_fully_adjudicated_gate15_only_ledger_can_be_ready(self):
        audit = audit_gate15_fidelity(
            _synthetic_markdown(),
            _synthetic_final_payload(),
            gate14_complete=True,
        )

        self.assertEqual(audit.active_gap_count, 2)
        self.assertEqual(audit.ledger_item_count, 2)
        self.assertEqual(audit.gate14_prerequisite_items, ())
        self.assertTrue(audit.all_gate15_items_final)
        self.assertTrue(audit.all_fallback_claims_fail_closed)
        self.assertTrue(audit.declared_complete)
        self.assertTrue(audit.gate15_ready)

    def test_final_ledger_still_requires_gate14_to_be_complete(self):
        payload = _synthetic_final_payload(declared=False)
        audit = audit_gate15_fidelity(
            _synthetic_markdown(),
            payload,
            gate14_complete=False,
        )

        self.assertTrue(audit.all_gate15_items_final)
        self.assertFalse(audit.gate14_complete)
        self.assertFalse(audit.gate15_ready)

    def test_parser_rejects_duplicate_active_gap_names(self):
        markdown = _synthetic_markdown().replace(
            "| Second gap | bounded behavior | exact behavior unresolved | 15 or later fidelity work |",
            "| First gap | bounded behavior | exact behavior unresolved | 15 |",
        )

        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "duplicate names",
        ):
            parse_active_fidelity_gaps(markdown)

    def test_parser_requires_active_gap_table(self):
        with self.assertRaisesRegex(
            Gate15FidelityLedgerError,
            "missing Active gaps section",
        ):
            parse_active_fidelity_gaps("# Fidelity Gaps\n")


if __name__ == "__main__":
    unittest.main()
