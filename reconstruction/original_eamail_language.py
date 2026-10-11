"""Byte-authenticated shipped FM2001 EAMail language resources.

EnglishEAM.str / EnglishEAM.idx are original original-game strings, not
replacement text. The native transfer-message class virtual +0x18
(0x56FB70) reads a separate language buffer at 0x947AA0; +0x1C
(0x56FBA0) constructs a separate message description. The exact mapping
from those runtime call sites to language IDX entry has NOT yet been proven.
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
