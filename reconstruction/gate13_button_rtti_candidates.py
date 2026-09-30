"""Candidate MSVC x86 RTTI -> Complete Object Locator -> Button vftables.

Prior firsthand canonical executable analysis establishes the MSVC RTTI
family and the embedded TeamSelect type Button@ease_2001. The exact canonical
executable is mandatory via OriginalPE32.parse before using this utility.

This is a bounded *candidate discovery aid*: a matching decorated type name,
valid file-backed type descriptor, plausible COL/class hierarchy, a pointer
to that COL and code-like following slots narrow manual Ghidra adjudication.
They DO NOT prove actual vftable ownership, virtual slot roles, control
state/frame transitions or text placement; do not ship inferred UI states.
Private reports containing actual original addresses remain outside Git.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import struct

from gate13_button_source_trace import OriginalPE32, OriginalPETraceError


# The C++ class/namespace is grounded in prior original-executable RTTI
# research, not a reverse-engineered vftable offset or an atlas frame index.
BUTTON_TYPE_NAME = b".?AVButton@ease_2001@@"

# Canonical first-hand research/EXECUTABLE_ANALYSIS.md independently proves
# these exact PE32 VAs for TeamSelect, unlike the still-unrecovered Button
# class vftable. This known-positive reference calibrates the parser itself.
KNOWN_TEAMSELECT_TYPE_NAME = b".?AVPMain@TeamSelect@@"
KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA = 0x81EC10
KNOWN_TEAMSELECT_VFTABLE_VA = 0x7C7650


@dataclass(frozen=True)
class MSVCRTTIVftableCandidate:
    decorated_type_name: str
    type_descriptor_va: int
    col_va: int
    col_offset: int
    col_constructor_displacement: int
    class_hierarchy_descriptor_va: int
    vftable_va: int
    vftable_col_pointer_va: int
    candidate_code_slots: tuple[dict, ...]
    classification: str = "MSVC_x86_RTTI_pattern_candidate_manual_CFG_required"


def _data_sections(pe: OriginalPE32):
    """Exclude .text from literal type strings, RTTI pointers and vftables."""
    return tuple(section for section in pe.sections if section.name != ".text")


def _find_aligned_pointer_data(pe: OriginalPE32, value: int):
    needle = struct.pack("<I", value)
    for section in _data_sections(pe):
        start = section.raw_offset
        blob = pe.data[start:start + section.file_backed_size]
        pos = 0
        while (pos := blob.find(needle, pos)) >= 0:
            va = pe.image_base + section.virtual_address + pos
            if va % 4 == 0:
                yield va
            pos += 1


def _mapped_data(pe: OriginalPE32, va: int, size: int) -> bool:
    try:
        section, _ = pe.section_for_va(va)
        if section.name == ".text":
            return False
        pe.read(va, size)
        return True
    except OriginalPETraceError:
        return False


def _type_descriptors(pe: OriginalPE32, decorated_name: bytes):
    if (not decorated_name or not decorated_name.endswith(b"@@")
            or b"\x00" in decorated_name):
        raise OriginalPETraceError("Expected a complete decorated RTTI class name")
    needle = decorated_name + b"\x00"
    for section in _data_sections(pe):
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        pos = 0
        while (pos := blob.find(needle, pos)) >= 0:
            name_va = pe.image_base + section.virtual_address + pos
            descriptor_va = name_va - 8  # MSVC i386: pVFTable, spare, name[]
            if (descriptor_va % 4 == 0
                    and _mapped_data(pe, descriptor_va, 8 + len(needle))):
                yield descriptor_va
            pos += 1


def discover_msvc_button_vftables(
    pe: OriginalPE32,
    *,
    decorated_name: bytes = BUTTON_TYPE_NAME,
    max_vftables: int = 16,
    max_slots: int = 24,
) -> tuple[MSVCRTTIVftableCandidate, ...]:
    """Find source-file-backed *potential* class vftables, not slot meanings.

    Production callers must pass the canonical SHA-gated OriginalPE32.parse
    result. Tiny synthetic fixtures use its documented expected_sha256 override.
    Every pointer chain is inspected in a bounded non-code PE section.
    """
    if type(max_vftables) is not int or not 1 <= max_vftables <= 64:
        raise OriginalPETraceError("max_vftables must be 1..64")
    if type(max_slots) is not int or not 1 <= max_slots <= 64:
        raise OriginalPETraceError("max_slots must be 1..64")
    result: list[MSVCRTTIVftableCandidate] = []
    visited = set()
    for td_va in _type_descriptors(pe, decorated_name):
        # MSVC x86 COL signature, subobject offset and constructor
        # displacement are three uint32s preceding pTypeDescriptor.
        for td_pointer_va in _find_aligned_pointer_data(pe, td_va):
            col_va = td_pointer_va - 12
            if not _mapped_data(pe, col_va, 20):
                continue
            sig, subobject_offset, cd_offset, ptd, chd = struct.unpack(
                "<IIIII", pe.read(col_va, 20)
            )
            if sig != 0 or ptd != td_va or subobject_offset > 0x100000:
                continue
            # A readable CHD with at least one base-class descriptor
            # rules out many accidental appearances of the raw pointer.
            if not _mapped_data(pe, chd, 16):
                continue
            ch_sig, attributes, base_count, base_ptr = struct.unpack(
                "<IIII", pe.read(chd, 16)
            )
            if ch_sig != 0 or not 1 <= base_count <= 128:
                continue
            if not _mapped_data(pe, base_ptr, base_count * 4):
                continue
            for col_pointer_va in _find_aligned_pointer_data(pe, col_va):
                vftable_va = col_pointer_va + 4
                if not _mapped_data(pe, col_pointer_va, 8):
                    continue
                if vftable_va in visited:
                    continue
                section, offset = pe.section_for_va(vftable_va)
                available = min(max_slots,
                                (section.file_backed_size - offset) // 4)
                slots = []
                for i in range(available):
                    slot_va = vftable_va + i * 4
                    code_va = struct.unpack("<I", pe.read(slot_va, 4))[0]
                    try:
                        target, _ = pe.section_for_va(code_va)
                        if target.name != ".text":
                            break
                    except OriginalPETraceError:
                        break
                    slots.append({
                        "index_unconfirmed": i,
                        "entry_va": slot_va,
                        "target_va_unconfirmed": code_va,
                    })
                if not slots:
                    continue
                visited.add(vftable_va)
                result.append(MSVCRTTIVftableCandidate(
                    decorated_type_name=decorated_name.decode("ascii"),
                    type_descriptor_va=td_va,
                    col_va=col_va,
                    col_offset=subobject_offset,
                    col_constructor_displacement=cd_offset,
                    class_hierarchy_descriptor_va=chd,
                    vftable_va=vftable_va,
                    vftable_col_pointer_va=col_pointer_va,
                    candidate_code_slots=tuple(slots),
                ))
                if len(result) >= max_vftables:
                    return tuple(result)
    return tuple(result)


def calibrate_against_known_rtti(
    pe: OriginalPE32,
    *,
    reference_name: bytes = KNOWN_TEAMSELECT_TYPE_NAME,
    expected_type_descriptor_va: int = KNOWN_TEAMSELECT_TYPE_DESCRIPTOR_VA,
    expected_vftable_va: int = KNOWN_TEAMSELECT_VFTABLE_VA,
) -> dict:
    """Cross-check the *same pattern decoder* against a known exact-source class.

    False means source layout, search assumptions, decorated type spelling,
    or the candidate scanner must be re-examined. It does NOT mean the
    original game's known reference addresses are disproven.
    The override points are solely for independent miniature PE32 tests.
    """
    known_candidates = discover_msvc_button_vftables(
        pe, decorated_name=reference_name,
    )
    matches = [
        item for item in known_candidates
        if item.type_descriptor_va == expected_type_descriptor_va
        and item.vftable_va == expected_vftable_va
    ]
    return {
        "known_reference_decorated_name": reference_name.decode("ascii"),
        "previously_proven_type_descriptor_va": expected_type_descriptor_va,
        "previously_proven_vftable_va": expected_vftable_va,
        "candidate_count": len(known_candidates),
        "expected_pair_recovered_by_same_pattern_decoder": len(matches) == 1,
        "evidence_limit": (
            "Only calibrates MSVC x86 RTTI scanning against independently "
            "recorded canonical TeamSelect anchors. Does not establish "
            "unknown Button class vftable ownership or virtual method roles."
        ),
    }


def button_rtti_candidate_report(
    pe: OriginalPE32, *,
    decorated_name: bytes = BUTTON_TYPE_NAME,
    max_vftables: int = 16,
    max_slots: int = 24,
) -> dict:
    candidates = discover_msvc_button_vftables(
        pe, decorated_name=decorated_name,
        max_vftables=max_vftables, max_slots=max_slots,
    )
    return {
        "source_sha256": pe.sha256,
        "known_original_teamselect_rtti_calibration":
            calibrate_against_known_rtti(pe),
        "decorated_class_search": decorated_name.decode("ascii"),
        "candidate_count": len(candidates),
        "candidates_not_validated_vtables": [asdict(c) for c in candidates],
        "evidence_limit": (
            "File-backed MSVC x86 decorated name, plausible RTTI COL/CHD "
            "pointer chain, and consecutive code-like vftable slots only. "
            "Manual original executable RTTI/CFG verification must establish "
            "actual Button class ownership and each virtual draw/update role. "
            "A state bit or virtual entry is NOT a proven source atlas frame."
        ),
    }
