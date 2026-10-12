"""Original SupportStaff label switch, source-indexed from shipped English files.

Native 0x4CDCD0 accepts 1..16, branches via jump table 0x4CDD84,
and reads string pointer globals initialized at 0x6458B0..0x645AF9.
Native ordinal 13 reads separate 0x9821E4, source independently resolved
from English.idx position 2437: 'Physiotherapist'.

Original CSupportStaff constructor 0x4CA2F0 stores the passed type at +0x04,
vtable 0x7C6834+0x14 resolves 0x42CB40 which returns that very type,
and PSupportStart 0x4D0725 passes the result to 0x4CDCD0. Native generated
staff type and localized ordinal therefore match, not a guessed alias.
This does not certify full GUI, staff name text or Windows acceptance.
"""
from __future__ import annotations

from ea_language_strings import EAStringIndex, EAStringTable
from support_staff import SupportStaffState

# Exact native switch entries from 0x4CDD84 and original English.idx's
# ordinal-to-string IDs. Source 0x64E320 resolves these at startup.
# The source role-label CASE is separate from the staff object type.
SOURCE_NATIVE_STAFF_LABEL_INDEX = {
    **{ordinal: 1876 + ordinal for ordinal in range(1, 13)},
    13: 2437,
    14: 1890,
    15: 1893,
    16: 1894,
}
SOURCE_NATIVE_STAFF_SPECIAL_CASE_13_GLOBAL = 0x9821E4


def original_supportstart_native_staff_label(
    native_label_case: int, strings: EAStringTable, indices: EAStringIndex,
) -> str | None:
    """Resolve verified original string for native 0x4CDCD0 case 1..16.

    The exceptional case13 uses 0x9821E4, but its independent index2437
    resolves to the shipped 'Physiotherapist' string; do not substitute
    the adjacent Support/Masseur string. Unknown ordinals return None.
    """
    if type(native_label_case) is not int:
        raise TypeError("Require the original native 0x4CDCD0 label ordinal")
    if type(strings) is not EAStringTable or type(indices) is not EAStringIndex:
        raise TypeError("Require validated original EA string and index tables")
    index = SOURCE_NATIVE_STAFF_LABEL_INDEX.get(native_label_case)
    if index is None:
        return None
    if not 0 <= index < len(indices.string_ids):
        raise ValueError("Original English.idx missing source label index")
    return indices.resolve(strings, index)



def original_supportstart_staff_type_label(
    staff: SupportStaffState, strings: EAStringTable, indices: EAStringIndex,
) -> str | None:
    """Source constructor/type getter→native original 0x4CDCD0 role text.

    Original 0x4CA2F0 puts the real staff type into CSupportStaff+0x04;
    0x7C6834+0x14 → 0x42CB40 returns [ecx+0x04] unchanged;
    PSupportStart 0x4D0725 sends that integer to 0x4CDCD0.
    This is NOT the synthetic staff display name, monthly cost, or GUI.
    """
    if type(staff) is not SupportStaffState:
        raise TypeError("Expected source-bounded CSupportStaff record")
    return original_supportstart_native_staff_label(staff.staff_type, strings, indices)
