"""Byte-authenticated shipped FM2001 EAMail language resources.

EnglishEAM.str / EnglishEAM.idx are original original-game strings, not
replacement text. The native transfer-message class virtual +0x18
(0x56FB70) reads a separate language buffer at 0x947AA0; +0x1C
(0x56FBA0) constructs a separate message description. The exact source mapping for the initial transfer-request title and
argument-zero message *template* is proven, but runtime phrase/manager/player
substitution and the final visible body remain unqualified.
Never choose a template by substring, guessed class name or modern category.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea_language_strings import EAStringIndex, EAStringTable, parse_language_pair


class OriginalEAMailLanguageError(ValueError):
    """Original source language pair is absent, altered or unqualified."""


ORIGINAL_EAMAIL_STR_PATH = "EnglishEAM.str"
ORIGINAL_EAMAIL_IDX_PATH = "EnglishEAM.idx"
ORIGINAL_EAMAIL_STR_SIZE = 298747
ORIGINAL_EAMAIL_IDX_SIZE = 5754
ORIGINAL_EAMAIL_STR_SHA256 = (
    "98387ef673e87a02cf2cab7349770a4415f29fd381877b603922302c3e3f174f"
)
ORIGINAL_EAMAIL_IDX_SHA256 = (
    "bd0e2b804f1ce85011509ff828cdc70f2409509537ec61a012d1fa0175932367"
)
ORIGINAL_EAMAIL_STRING_COUNT = 1609
ORIGINAL_EAMAIL_INDEX_COUNT = 2877

# Exact native +0x18 title source:
# - 0x50D5A7/0x50D5B6 pass literal "englisheam.idx" to 0x5B65A0;
# - it issues exactly 2,877 sequential 2-byte fread(0x667E90) calls;
# - 0x64E320 binds pointer slots 0x87AC28, 0x87AC24 ... 0x877F38;
# - 0x8797A4 is the 1,314th slot, zero-based index 1313;
# - EAMPlayerAskTransferListsub virtual +0x18 = 0x56FB70,
#   dereferencing that exact slot, then formatting from its string pointer.
# - EnglishEAM.idx[1313] = original string 942 = "Transfer List".
# SHA-qualified EnglishEAM source bytes are required; never hardcode a
# modern translation or silently substitute that literal at rendering.
ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_SLOT_VA = 0x8797A4
ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_VIRTUAL_VA = 0x56FB70
ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_IDX_ORDINAL = 1313
ORIGINAL_TRANSFER_LIST_SUBJECT_STRING_ID = 942
ORIGINAL_TRANSFER_LIST_SUBJECT_VERIFIED_TEXT = "Transfer List"

# Original +0x1C body preview source (NOT the final interpolated string):
# 0x56FBA0, argument zero -> 0x56FD65 -> 0x56FE06 dereferences
# mapped EnglishEAM pointer 0x8797A0. The original 2877-entry loader
# places this at ordinal (0x87AC28-0x8797A0)/4 = 1314; IDX[1314]
# and IDX[1315] both refer to the same original STR string ID 943.
# Original native 0x612FD0/0x659810 interpolation also requires actual
# typed player, manager, phrase and record-specific state; never invent it.
ORIGINAL_TRANSFER_LIST_BODY_NATIVE_SLOT_VA = 0x8797A0
ORIGINAL_TRANSFER_LIST_BODY_NATIVE_VIRTUAL_VA = 0x56FBA0
ORIGINAL_TRANSFER_LIST_BODY_NATIVE_IDX_ORDINAL = 1314
ORIGINAL_TRANSFER_LIST_BODY_STRING_ID = 943
ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE = "Dear {MANAGERNAME:1}<P><P>{PHRASE:PLAYERASKTRANSFERLISTREASON}<P><P><P>Yours Sincerely,<P><P>{PLAYERNAME:1}"


@dataclass(frozen=True)
class VerifiedOriginalEAMailLanguage:
    strings: EAStringTable
    index: EAStringIndex

    def source_selected_template(
        self, index_entry: int, *, original_selector_proven: bool
    ) -> str:
        """Only resolve an original index when a native selector proves it.

        Original text is not a substitute for source-verified per-message
        choice, typed player reference, original string interpolation or GUI.
        """
        if (type(original_selector_proven) is not bool
                or not original_selector_proven):
            raise OriginalEAMailLanguageError(
                "Native source IDX selector for this record is not proven"
            )
        if type(index_entry) is not int or not 0 <= index_entry < len(self.index.string_ids):
            raise OriginalEAMailLanguageError("Native IDX selection is out of bounds")
        return self.index.resolve(self.strings, index_entry)

    def original_player_asks_transfer_list_body_template(self) -> str:
        """Source original +0x1C argument-zero template, NOT a rendered preview.

        Original 0x56FE06 accesses slot 0x8797A0, ordinal 1314 of
        EnglishEAM.idx. Native substitution and text formatting are separate;
        callers must not display an unresolved {PHRASE:...} marker as a body.
        """
        ordinal = ORIGINAL_TRANSFER_LIST_BODY_NATIVE_IDX_ORDINAL
        if (self.index.string_ids[ordinal] != ORIGINAL_TRANSFER_LIST_BODY_STRING_ID
                or self.strings[ORIGINAL_TRANSFER_LIST_BODY_STRING_ID]
                != ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE):
            raise OriginalEAMailLanguageError(
                "Native PlayerAskTransferList body template no longer matches original source"
            )
        return self.index.resolve(self.strings, ordinal)

    def original_player_asks_transfer_list_subject(self) -> str:
        """Exact original EAMPlayerAskTransferListsub +0x18 caption.

        Unlike arbitrary guessed EAM localized templates, this index was
        traced through the original 2,877-call native EnglishEAM.idx loader,
        per-pointer slot 0x8797A4, class vft +0x18 and the source IDX+STR.
        Do not extrapolate this English caption to other languages/classes,
        the +0x1C message body, or live mutable native read flags.
        """
        source_entry = ORIGINAL_TRANSFER_LIST_SUBJECT_NATIVE_IDX_ORDINAL
        expected_id = ORIGINAL_TRANSFER_LIST_SUBJECT_STRING_ID
        if (self.index.string_ids[source_entry] != expected_id
                or self.strings[expected_id]
                != ORIGINAL_TRANSFER_LIST_SUBJECT_VERIFIED_TEXT):
            raise OriginalEAMailLanguageError(
                "Native PlayerAskTransferList subject lookup no longer matches original source"
            )
        return self.index.resolve(self.strings, source_entry)


def load_verified_original_eamail_language(
    original_source_root: str | Path,
) -> VerifiedOriginalEAMailLanguage:
    """Read byte-identical original pair; no synthetic missing-file fallbacks."""
    root = Path(original_source_root)
    files = (
        (ORIGINAL_EAMAIL_STR_PATH, ORIGINAL_EAMAIL_STR_SIZE, ORIGINAL_EAMAIL_STR_SHA256),
        (ORIGINAL_EAMAIL_IDX_PATH, ORIGINAL_EAMAIL_IDX_SIZE, ORIGINAL_EAMAIL_IDX_SHA256),
    )
    raw: list[bytes] = []
    for name, expected_size, expected_hash in files:
        try:
            source = (root / name).read_bytes()
        except FileNotFoundError as exc:
            raise OriginalEAMailLanguageError(
                f"Original EAM localization file is missing: {name}"
            ) from exc
        if len(source) != expected_size or sha256(source).hexdigest() != expected_hash:
            raise OriginalEAMailLanguageError(
                f"Original EAM localization source bytes differ: {name}"
            )
        raw.append(source)
    table, index = parse_language_pair(*raw)
    if (len(table.strings) != ORIGINAL_EAMAIL_STRING_COUNT
            or len(index.string_ids) != ORIGINAL_EAMAIL_INDEX_COUNT):
        raise OriginalEAMailLanguageError(
            "Original EAM language mapping table shape changed"
        )
    return VerifiedOriginalEAMailLanguage(table, index)
