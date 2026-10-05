"""Private checksum-gated source trace for Gate-15 support-staff cost value.

Persisted source research already proves that day-of-month 1 reaches
0x4CA0F0, walks the DBRUser CSupportStaff lists, calls virtual slot +0x24 on
each staff object, multiplies that returned value by 1000.0 and 1/12, and
posts the result as Balance category 102 / flag 1.

The remaining fidelity boundary is narrower: the clean-room runtime does not
materialize the original value returned by CSupportStaff virtual +0x24. This
read-only tracer resolves the canonical vtable slot target and emits bounded
private windows around that target and the already-proven monthly caller.

Resolving a vtable pointer is not semantic proof of the target's field layout,
units, mutability, constructor initialization, or save/load behavior. Generated
original executable bytes/disassembly must remain private outside Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)


class Gate15SupportStaffCostTraceError(OriginalPETraceError):
    pass


MONTHLY_SUPPORT_STAFF_COST_ROUTINE_VA = 0x4CA0F0
CSUPPORTSTAFF_CONSTRUCTOR_VA = 0x4CA610
GENERIC_SUPPORT_STAFF_GENERATOR_VA = 0x4C98B0
FIXED_SUPPORT_STAFF_GENERATOR_VA = 0x4C9D40
CSUPPORTSTAFF_VTABLE_VA = 0x7C6834

# Previously source-qualified virtual roles. The +0x24 target is the unresolved
# amount producer needed by category-102 monthly staff costs.
CSUPPORTSTAFF_TYPE_VIRTUAL_OFFSET = 0x14
CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET = 0x24
CSUPPORTSTAFF_TRAINING_RATING_VIRTUAL_OFFSET = 0x40

KNOWN_SLOT_ROLES = (
    ("staff_type", CSUPPORTSTAFF_TYPE_VIRTUAL_OFFSET, True),
    ("monthly_cost_value", CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET, False),
    ("effective_training_rating", CSUPPORTSTAFF_TRAINING_RATING_VIRTUAL_OFFSET, True),
)

STATIC_TRACE_WINDOWS = (
    ("monthly support-staff category-102 caller", MONTHLY_SUPPORT_STAFF_COST_ROUTINE_VA, 0x180),
    ("CSupportStaff constructor", CSUPPORTSTAFF_CONSTRUCTOR_VA, 0x140),
    ("generic support-staff generator", GENERIC_SUPPORT_STAFF_GENERATOR_VA, 0x180),
    ("fixed fresh-user support-staff generator", FIXED_SUPPORT_STAFF_GENERATOR_VA, 0x180),
)


def resolve_vtable_slot_target(
    pe: OriginalPE32,
    vtable_va: int,
    slot_offset: int,
) -> dict:
    """Resolve one canonical vtable entry without assigning new semantics."""
    if type(vtable_va) is not int or not 0 <= vtable_va < 1 << 32:
        raise Gate15SupportStaffCostTraceError("vtable_va must be uint32")
    if (
        type(slot_offset) is not int
        or slot_offset < 0
        or slot_offset > 0x400
        or slot_offset % 4
    ):
        raise Gate15SupportStaffCostTraceError(
            "slot_offset must be a 4-byte-aligned offset within 0x000..0x400"
        )

    vtable_section, _ = pe.section_for_va(vtable_va + slot_offset)
    target_va = struct.unpack("<I", pe.read(vtable_va + slot_offset, 4))[0]
    target_section, _ = pe.section_for_va(target_va)
    if target_section.name != ".text":
        raise Gate15SupportStaffCostTraceError(
            f"vtable slot +0x{slot_offset:X} does not resolve into .text"
        )
    return {
        "vtable_va": vtable_va,
        "slot_offset": slot_offset,
        "entry_va": vtable_va + slot_offset,
        "entry_section": vtable_section.name,
        "target_va": target_va,
        "target_section": target_section.name,
        "classification": "resolved_vtable_pointer_not_new_semantic_proof",
    }


def support_staff_cost_trace_report(
    pe: OriginalPE32,
    *,
    windows=STATIC_TRACE_WINDOWS,
    slot_roles=KNOWN_SLOT_ROLES,
    with_disassembly: bool = False,
    target_window_size: int = 0x100,
) -> dict:
    """Collect the exact unresolved support-staff cost source boundary."""
    if type(with_disassembly) is not bool:
        raise Gate15SupportStaffCostTraceError("with_disassembly must be boolean")
    if (
        type(target_window_size) is not int
        or not 0x10 <= target_window_size <= 0x1000
    ):
        raise Gate15SupportStaffCostTraceError(
            "target_window_size must be within 0x10..0x1000"
        )

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate15SupportStaffCostTraceError(
                "trace windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate15SupportStaffCostTraceError("invalid support-staff trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate15SupportStaffCostTraceError(
                f"{label}: expected source-qualified code window in .text"
            )
        blob = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "requested_size": requested_size,
                "actual_window_bytes": len(blob),
                "section": section.name,
                "raw_hex": blob.hex(),
                "linear_disassembly_only": (
                    tuple(disassemble_window(blob, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": "bounded_source_window_not_function_boundary",
            }
        )

    slots = []
    for item in tuple(slot_roles):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate15SupportStaffCostTraceError(
                "slot roles must be (label, slot_offset, role_previously_recovered)"
            )
        label, slot_offset, role_previously_recovered = item
        if (
            not isinstance(label, str)
            or not label
            or type(role_previously_recovered) is not bool
        ):
            raise Gate15SupportStaffCostTraceError("invalid support-staff slot role")
        resolved = resolve_vtable_slot_target(
            pe,
            CSUPPORTSTAFF_VTABLE_VA,
            slot_offset,
        )
        target_blob = pe.bounded_window(
            resolved["target_va"],
            target_window_size,
        )
        resolved.update(
            {
                "role_label": label,
                "role_previously_recovered": role_previously_recovered,
                "target_window_bytes": len(target_blob),
                "target_raw_hex": target_blob.hex(),
                "target_linear_disassembly_only": (
                    tuple(disassemble_window(target_blob, resolved["target_va"]))
                    if with_disassembly
                    else None
                ),
            }
        )
        slots.append(resolved)

    cost_slot = next(
        row
        for row in slots
        if row["slot_offset"] == CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET
    )
    return {
        "source_sha256": pe.sha256,
        "c_support_staff_vtable_va": CSUPPORTSTAFF_VTABLE_VA,
        "monthly_support_staff_cost_routine_va": MONTHLY_SUPPORT_STAFF_COST_ROUTINE_VA,
        "monthly_cost_contract_already_recovered": {
            "day_of_month": 1,
            "staff_lists": ("DBRUser+0x5B8", "DBRUser+0x5C4"),
            "virtual_slot_offset": CSUPPORTSTAFF_COST_VALUE_VIRTUAL_OFFSET,
            "scale": 1000.0,
            "period_factor": "1/12",
            "balance_category": 102,
            "balance_flag": 1,
        },
        "windows": tuple(inspected),
        "vtable_slots": tuple(slots),
        "cost_virtual_target_va": cost_slot["target_va"],
        "cost_virtual_target_pointer_resolved": True,
        "cost_virtual_value_semantics_recovered": False,
        "cost_virtual_backing_field_recovered": False,
        "cost_virtual_constructor_initialization_recovered": False,
        "cost_virtual_save_load_roundtrip_recovered": False,
        "monthly_support_staff_amount_materialized": False,
        "gate15_support_staff_cost_gap_closed": False,
        "gate15_complete": False,
        "evidence_limit": (
            "The report resolves exact canonical CSupportStaff vtable pointers "
            "and bounded source windows only. Existing research already proves "
            "that monthly category-102 accounting calls slot +0x24 and applies "
            "value*1000/12. The target pointer/window alone does not prove the "
            "returned value's backing field, units, initialization, mutation, "
            "persistence, runtime materialization, or Gate 15 completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--target-window-size", type=lambda value: int(value, 0), default=0x100)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = support_staff_cost_trace_report(
        pe,
        with_disassembly=args.disassemble,
        target_window_size=args.target_window_size,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-15 support-staff cost trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
