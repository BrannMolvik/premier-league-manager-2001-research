"""Original SupportStaff label switch, source-indexed from shipped English files.

Native 0x4CDCD0 accepts 1..16, branches via jump table 0x4CDD84,
and reads string pointer globals initialized at 0x6458B0..0x645AF9.
Native ordinal 13 instead reads separate 0x9821E4 (not the contiguous
Support text family), so it is UNKNOWN until that source is qualified.

This is the 0x4CDCD0 label-ordinal contract. It is NOT proof of the
CSupportStaff virtual+0x14 ordinal for any particular generated staff,
a player-visible control, or the training behavior of staff_type fields.
"""
from __future__ import annotations

from ea_language_strings import EAStringIndex, EAStringTable

# Exact native switch entries from 0x4CDD84 and original English.idx's
# ordinal-to-string IDs. Source 0x64E320 resolves these at startup.
# The source role-label CASE is separate from the staff object type.
SOURCE_NATIVE_STAFF_LABEL_INDEX = {
    **{ordinal: 1876 + ordinal for ordinal in range(1, 13)},
    14: 1890,
    15: 1893,
    16: 1894,
}
SOURCE_NATIVE_STAFF_SPECIAL_CASE_13_GLOBAL = 0x9821E4


def original_supportstart_native_staff_label(
    native_label_case: int, strings: EAStringTable, indices: EAStringIndex,
) -> str | None:
    """Resolve verified original string for native 0x4CDCD0 case 1..16.

    Return None if the original case uses a different global or if caller
    lacks a proven ordinal. Do not silently guess the source text.
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
