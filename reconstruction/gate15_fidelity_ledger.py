"""Fail-closed coverage audit for the Gate-15 fidelity acceptance ledger.

Gate 15 requires every live row in research/FIDELITY_GAPS.md to be fixed,
proven irrelevant, or explicitly accepted/documented, while no deterministic
fallback may be described as original behavior. This module makes omission and
premature-completion failures machine-checkable without inventing source facts.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


class Gate15FidelityLedgerError(ValueError):
    pass


FINAL_STATUSES = frozenset(
    {
        "fixed",
        "proven_irrelevant",
        "accepted_documented",
    }
)
PRE_RELEASE_STATUSES = frozenset(
    {
        "pending_source_or_acceptance",
        "pending_final_acceptance",
        "prerequisite_gate_14",
    }
)
ALLOWED_STATUSES = FINAL_STATUSES | PRE_RELEASE_STATUSES


@dataclass(frozen=True)
class ActiveFidelityGap:
    gap: str
    planned_gate: str


@dataclass(frozen=True)
class Gate15FidelityLedgerItem:
    gap: str
    planned_gate: str
    owner_gate: int
    status: str
    fallback_described_as_original: bool
    release_limitation_required_if_accepted: bool

    def __post_init__(self) -> None:
        if not self.gap.strip():
            raise Gate15FidelityLedgerError("ledger gap name must be non-empty")
        if not self.planned_gate.strip():
            raise Gate15FidelityLedgerError(
                f"ledger planned gate must be non-empty for {self.gap}"
            )
        if self.owner_gate not in (14, 15):
            raise Gate15FidelityLedgerError(
                f"unsupported fidelity owner gate {self.owner_gate} for {self.gap}"
            )
        if self.status not in ALLOWED_STATUSES:
            raise Gate15FidelityLedgerError(
                f"unsupported fidelity status {self.status!r} for {self.gap}"
            )
        if type(self.fallback_described_as_original) is not bool:
            raise Gate15FidelityLedgerError(
                f"fallback-original flag must be boolean for {self.gap}"
            )
        if self.fallback_described_as_original:
            raise Gate15FidelityLedgerError(
                f"Gate 15 forbids fallback-as-original claims for {self.gap}"
            )
        if type(self.release_limitation_required_if_accepted) is not bool:
            raise Gate15FidelityLedgerError(
                f"release-limitation flag must be boolean for {self.gap}"
            )
        if self.owner_gate == 14 and self.status != "prerequisite_gate_14":
            raise Gate15FidelityLedgerError(
                f"Gate-14-owned gap must remain prerequisite_gate_14: {self.gap}"
            )
        if self.status == "prerequisite_gate_14" and self.owner_gate != 14:
            raise Gate15FidelityLedgerError(
                f"only Gate-14-owned gaps may use prerequisite_gate_14: {self.gap}"
            )
        if (
            self.status == "accepted_documented"
            and not self.release_limitation_required_if_accepted
        ):
            raise Gate15FidelityLedgerError(
                f"accepted fidelity gap must be carried to release limitations: {self.gap}"
            )


@dataclass(frozen=True)
class Gate15FidelityAudit:
    active_gap_count: int
    ledger_item_count: int
    missing_from_ledger: tuple[str, ...]
    unexpected_in_ledger: tuple[str, ...]
    planned_gate_mismatches: tuple[str, ...]
    status_counts: tuple[tuple[str, int], ...]
    gate14_prerequisite_items: tuple[str, ...]
    all_fallback_claims_fail_closed: bool
    gate14_complete: bool
    all_gate15_items_final: bool
    declared_complete: bool
    gate15_ready: bool


def parse_active_fidelity_gaps(markdown: str) -> tuple[ActiveFidelityGap, ...]:
    """Parse the live top-level table from FIDELITY_GAPS.md."""
    if not isinstance(markdown, str):
        raise Gate15FidelityLedgerError("fidelity gaps markdown must be text")
    marker = "## Active gaps"
    start = markdown.find(marker)
    if start < 0:
        raise Gate15FidelityLedgerError("missing Active gaps section")
    tail = markdown[start + len(marker):]
    next_heading = tail.find("\n## ")
    section = tail if next_heading < 0 else tail[:next_heading]

    rows: list[ActiveFidelityGap] = []
    header_seen = False
    separator_seen = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [part.strip() for part in line[1:-1].split("|")]
        if len(cells) < 4:
            raise Gate15FidelityLedgerError(
                f"malformed active-gap table row: {raw_line}"
            )
        first = cells[0]
        last = cells[-1]
        if first == "Gap":
            header_seen = True
            continue
        if first.startswith("---"):
            separator_seen = True
            continue
        if not first:
            raise Gate15FidelityLedgerError("active gap name must be non-empty")
        rows.append(ActiveFidelityGap(gap=first, planned_gate=last))

    if not header_seen or not separator_seen:
        raise Gate15FidelityLedgerError("active-gap table header is incomplete")
    if not rows:
        raise Gate15FidelityLedgerError("active-gap table contains no gaps")

    names = tuple(row.gap for row in rows)
    if len(set(names)) != len(names):
        raise Gate15FidelityLedgerError("active-gap table contains duplicate names")
    return tuple(rows)


def load_fidelity_ledger(payload: object) -> tuple[bool, tuple[Gate15FidelityLedgerItem, ...]]:
    if not isinstance(payload, dict):
        raise Gate15FidelityLedgerError("Gate-15 ledger must be a JSON object")
    if payload.get("schema_version") != 1:
        raise Gate15FidelityLedgerError("unsupported Gate-15 ledger schema")
    if payload.get("source_path") != "research/FIDELITY_GAPS.md":
        raise Gate15FidelityLedgerError("Gate-15 ledger source_path drifted")

    declared = payload.get("gate15_declared_complete")
    if type(declared) is not bool:
        raise Gate15FidelityLedgerError(
            "gate15_declared_complete must be boolean"
        )

    raw_items = payload.get("items")
    if type(raw_items) is not list or not raw_items:
        raise Gate15FidelityLedgerError("Gate-15 ledger requires item records")

    items: list[Gate15FidelityLedgerItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise Gate15FidelityLedgerError("Gate-15 ledger item must be object")
        try:
            item = Gate15FidelityLedgerItem(
                gap=raw["gap"],
                planned_gate=raw["planned_gate"],
                owner_gate=raw["owner_gate"],
                status=raw["status"],
                fallback_described_as_original=raw[
                    "fallback_described_as_original"
                ],
                release_limitation_required_if_accepted=raw[
                    "release_limitation_required_if_accepted"
                ],
            )
        except KeyError as exc:
            raise Gate15FidelityLedgerError(
                f"Gate-15 ledger item missing field {exc.args[0]}"
            ) from exc
        items.append(item)

    names = tuple(item.gap for item in items)
    if len(set(names)) != len(names):
        raise Gate15FidelityLedgerError("Gate-15 ledger contains duplicate gaps")
    return declared, tuple(items)


def audit_gate15_fidelity(
    markdown: str,
    ledger_payload: object,
    *,
    gate14_complete: bool,
) -> Gate15FidelityAudit:
    if type(gate14_complete) is not bool:
        raise Gate15FidelityLedgerError("gate14_complete must be boolean")

    gaps = parse_active_fidelity_gaps(markdown)
    declared, items = load_fidelity_ledger(ledger_payload)

    gap_map = {row.gap: row for row in gaps}
    item_map = {item.gap: item for item in items}
    missing = tuple(sorted(set(gap_map) - set(item_map)))
    unexpected = tuple(sorted(set(item_map) - set(gap_map)))

    mismatches = tuple(
        sorted(
            gap
            for gap in set(gap_map) & set(item_map)
            if gap_map[gap].planned_gate != item_map[gap].planned_gate
        )
    )

    counts: dict[str, int] = {}
    for item in items:
        counts[item.status] = counts.get(item.status, 0) + 1
    status_counts = tuple(sorted(counts.items()))

    gate14_items = tuple(
        item.gap for item in items if item.status == "prerequisite_gate_14"
    )
    gate15_items = tuple(item for item in items if item.owner_gate == 15)
    all_gate15_final = bool(gate15_items) and all(
        item.status in FINAL_STATUSES for item in gate15_items
    )
    all_fallbacks_fail_closed = all(
        not item.fallback_described_as_original for item in items
    )

    ready = (
        not missing
        and not unexpected
        and not mismatches
        and all_fallbacks_fail_closed
        and gate14_complete
        and not gate14_items
        and all_gate15_final
    )

    if declared and not ready:
        raise Gate15FidelityLedgerError(
            "Gate 15 cannot be declared complete while the fidelity audit is not ready"
        )

    return Gate15FidelityAudit(
        active_gap_count=len(gaps),
        ledger_item_count=len(items),
        missing_from_ledger=missing,
        unexpected_in_ledger=unexpected,
        planned_gate_mismatches=mismatches,
        status_counts=status_counts,
        gate14_prerequisite_items=gate14_items,
        all_fallback_claims_fail_closed=all_fallbacks_fail_closed,
        gate14_complete=gate14_complete,
        all_gate15_items_final=all_gate15_final,
        declared_complete=declared,
        gate15_ready=ready,
    )


def audit_repository_gate15(
    repository_root: str | Path,
    *,
    gate14_complete: bool,
) -> Gate15FidelityAudit:
    root = Path(repository_root)
    markdown = (root / "research" / "FIDELITY_GAPS.md").read_text(
        encoding="utf-8"
    )
    payload = json.loads(
        (root / "research" / "GATE15_FIDELITY_ACCEPTANCE_LEDGER.json").read_text(
            encoding="utf-8"
        )
    )
    return audit_gate15_fidelity(
        markdown,
        payload,
        gate14_complete=gate14_complete,
    )
