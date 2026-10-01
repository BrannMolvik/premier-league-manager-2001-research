"""Bounded canonical-executable trace aid for unresolved Gate 13 Squad bindings.

This tool starts only from Squad class/method anchors already proven against the
canonical FM2001 executable. It does not assign player-list column meanings,
status icon meanings, FormationText frame meanings, or native state names.
Reports contain original instruction/pointer evidence and must remain private
outside Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)
from gate13_button_vtable_xref_candidates import (
    linear_direct_branch_candidates,
    screen_vtable_candidates,
)
from original_squad_resources import (
    CBASE_PLAYER_LIST_VFTABLE_VA,
    FORMATION_TEXT_BAR_SETUP_VA,
    FORMATION_TEXT_FORM_SETUP_VA,
    FORMATION_TEXT_VFTABLE_VA,
    SQUAD_PITCH_SETUP_VA,
    SQUAD_PITCH_VFTABLE_VA,
    SQUAD_SCREEN_EVENT_HANDLER_VA,
    SQUAD_SCREEN_SETUP_VA,
    SQUAD_SCREEN_VFTABLE_VA,
)


SQUAD_VTABLE_SEEDS = (
    ("CBasePlayerList class vtable", CBASE_PLAYER_LIST_VFTABLE_VA),
    ("FormationText class vtable", FORMATION_TEXT_VFTABLE_VA),
    ("PSquadPitch class vtable", SQUAD_PITCH_VFTABLE_VA),
    ("PSquadScreen class vtable", SQUAD_SCREEN_VFTABLE_VA),
)

# These are bounded inspection windows anchored at already-proven entry points.
# Sizes are analyst windows, not claims about exact function boundaries.
SQUAD_TRACE_WINDOWS = (
    ("PSquadPitch setup / FormationText row construction", SQUAD_PITCH_SETUP_VA, 0x500),
    ("FormationText squad_bars setup", FORMATION_TEXT_BAR_SETUP_VA, 0xD0),
    ("FormationText squad_form_anim setup", FORMATION_TEXT_FORM_SETUP_VA, 0xE0),
    ("PSquadScreen setup / roster construction", SQUAD_SCREEN_SETUP_VA, 0x500),
    ("PSquadScreen event handler / view switching", SQUAD_SCREEN_EVENT_HANDLER_VA, 0x300),
)

SQUAD_CODE_SEEDS = tuple((label, va) for label, va, _ in SQUAD_TRACE_WINDOWS)


def squad_trace_report(
    pe: OriginalPE32,
    *,
    with_disassembly: bool = False,
    windows: tuple[tuple[str, int, int], ...] = SQUAD_TRACE_WINDOWS,
    vtable_seeds: tuple[tuple[str, int], ...] = SQUAD_VTABLE_SEEDS,
    entries_per_vtable: int = 24,
) -> dict:
    """Return bounded private evidence without promoting candidate semantics."""
    inspected = []
    for label, start_va, requested_size in windows:
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise OriginalPETraceError(
                f"{label}: expected previously proven code anchor to map to .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        decoded = disassemble_window(raw, start_va) if with_disassembly else None
        inspected.append({
            "label": label,
            "start_va": start_va,
            "section": section.name,
            "window_bytes": len(raw),
            "raw_hex": raw.hex(),
            "linear_disassembly_only": decoded,
        })

    slots = screen_vtable_candidates(
        pe, seeds=vtable_seeds, entries_per_seed=entries_per_vtable
    )
    slot_rows = [
        {
            "seed": item.seed,
            "entry_index": item.entry_index,
            "entry_va": item.entry_va,
            "value": item.value,
            "mapped_section": item.mapped_section,
            "plausible_text_pointer": item.plausible_text_pointer,
        }
        for item in slots
    ]
    plausible = tuple(
        (
            f"{item.seed} sequential slot {item.entry_index} candidate",
            item.value,
        )
        for item in slots
        if item.plausible_text_pointer
    )

    branch_leads = None
    if with_disassembly:
        branch_leads = list(
            linear_direct_branch_candidates(
                pe,
                targets=tuple(SQUAD_CODE_SEEDS) + plausible,
                max_candidates=256,
            )
        )

    return {
        "source_sha256": pe.sha256,
        "evidence_limit": (
            "Bounded canonical source bytes, sequential class-vtable pointer "
            "candidates, and optional linear direct-branch leads only. "
            "CBasePlayerList row/column/status meanings and FormationText "
            "state-to-frame semantics require manual CFG/data-flow adjudication "
            "before they may be promoted."
        ),
        "windows": inspected,
        "seed_vtables": [
            {"seed": label, "seed_va": va} for label, va in vtable_seeds
        ],
        "raw_vtable_slots": slot_rows,
        "linear_direct_branch_candidates": branch_leads,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Private JSON report outside the Git repository",
    )
    parser.add_argument(
        "--disassemble",
        action="store_true",
        help="Include bounded Capstone linear disassembly and direct-branch leads",
    )
    parser.add_argument(
        "--vtable-slots",
        type=int,
        default=24,
        help="Sequential candidate slots per already-proven class vtable (1..64)",
    )
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = squad_trace_report(
        pe,
        with_disassembly=args.disassemble,
        entries_per_vtable=args.vtable_slots,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate 13 Squad trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
