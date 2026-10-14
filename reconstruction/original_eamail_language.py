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


# 0x56FD65 creates a PHRASE:PLAYERASKTRANSFERLISTREASON native token
# with +0x10 = record+0x3C reason. Its +0x00 dispatcher table at 0x7D6200
# selects 0x60FE40: cases 1..7 jump to native language slots
# 0x87A70C, 0x87A708, ... 0x87A6F4 (EnglishEAM IDX 327..333).
ORIGINAL_TRANSFER_REASON_DISPATCH_VA = 0x60FE40
ORIGINAL_TRANSFER_REASON_TOKEN_LITERAL_VA = 0x8327FC
ORIGINAL_TRANSFER_REASON_FIRST_SLOT_VA = 0x87A70C
ORIGINAL_TRANSFER_REASON_FIRST_IDX_ORDINAL = 327
ORIGINAL_TRANSFER_REASON_STRING_IDS = (326, 327, 328, 329, 330, 331, 332)


def native_transfer_reason_from_crt_draw(rand15: int) -> int:
    """Original 0x56FDD0..0x56FDF9 signed quotient, WITHOUT drawing RNG.

    Original 0x66951C returns 0..32767. The native multiply-by-seven,
    signed 0x80010003 quotient /32767 and zero->one substitution agree
    for all 32768 inputs. Shared RNG ownership/call timing is separate.
    """
    if type(rand15) is not int or not 0 <= rand15 <= 0x7FFF:
        raise OriginalEAMailLanguageError("Original EAM reason needs 15-bit CRT output")
    return max(1, (rand15 * 7) // 32767)


# SOURCE-ONLY ORIGINAL 0x606540 injury notice +0x18 title callbacks.
# Verified against the exact private PE SHA833bf95e and EnglishEAM STR/IDX
# SHA98387ef6/bd0e2b80. Key is constructor entry; values are
# (concrete vtable, native virtual+0x0C tag, virtual+0x18 function,
#  EnglishEAM loader ordinal, original STR ID).
# This is not a native constructor execution, 413020 delivery, or GUI row.
ORIGINAL_606540_TITLE_ROUTES = {
    0x58AA70: (0x7D1CE0, 243, 0x58AB00, 1803, 1153),
    0x58AD80: (0x7D1D34, 244, 0x58AE10, 1808, 1153),
    0x58B090: (0x7D1D88, 245, 0x58B130, 1813, 1158),
    0x58B360: (0x7D1DDC, 246, 0x58B3F0, 1818, 1153),
    0x58B670: (0x7D1E30, 247, 0x58B700, 1823, 1153),
    0x58B980: (0x7D1E84, 248, 0x58BA20, 1828, 1158),
    0x58BB90: (0x7D1ED8, 249, 0x58BC20, 1833, 1153),
    0x58BEA0: (0x7D1F2C, 250, 0x58BF30, 1838, 1153),
    0x58C1B0: (0x7D1F80, 251, 0x58C250, 1843, 1158),
    0x59F8E0: (0x7D422C, 359, 0x59F970, 2383, 1153),
    0x59FBF0: (0x7D4280, 360, 0x59FC90, 2388, 1158),
    0x59FEC0: (0x7D42D4, 361, 0x59FF50, 2393, 1153),
    0x5A01D0: (0x7D4328, 362, 0x5A0260, 2398, 1153),
    0x5A04E0: (0x7D437C, 363, 0x5A0570, 2403, 1153),
    0x5A07F0: (0x7D43D0, 364, 0x5A0890, 2408, 1158),
}
ORIGINAL_606540_TITLE_SOURCE_TEXTS = {
    1153: "Ankle injury to {PLAYERNAME:1}",
    1158: "Ankle injury",
}


# Original 15 concrete virtual+0x1C body callbacks, each using native
# selector argument 0, 1 or 2. Values: (vtable, callback, first IDX ordinal,
# (STR IDs for variant0, variant1, variant2)). Native input origin, typed
# substitutions and display/receipt are NOT established by this selector.
ORIGINAL_606540_BODY_ROUTES = {
    0x58AA70: (0x7D1CE0, 0x58AB80, 1804, (1154, 1154, 1154)),
    0x58AD80: (0x7D1D34, 0x58AE90, 1809, (1156, 1156, 1156)),
    0x58B090: (0x7D1D88, 0x58B160, 1814, (1159, 1159, 1159)),
    0x58B360: (0x7D1DDC, 0x58B470, 1819, (1161, 1161, 1161)),
    0x58B670: (0x7D1E30, 0x58B780, 1824, (1163, 1163, 1163)),
    0x58B980: (0x7D1E84, 0x58BA50, 1829, (1165, 1165, 1165)),
    0x58BB90: (0x7D1ED8, 0x58BCA0, 1834, (1167, 1167, 1167)),
    0x58BEA0: (0x7D1F2C, 0x58BFB0, 1839, (1169, 1170, 1170)),
    0x58C1B0: (0x7D1F80, 0x58C280, 1844, (1172, 1172, 1172)),
    0x59F8E0: (0x7D422C, 0x59F9F0, 2384, (1432, 1432, 1432)),
    0x59FBF0: (0x7D4280, 0x59FCC0, 2389, (1433, 1433, 1433)),
    0x59FEC0: (0x7D42D4, 0x59FFD0, 2394, (1434, 1434, 1434)),
    0x5A01D0: (0x7D4328, 0x5A02E0, 2399, (1161, 1161, 1161)),
    0x5A04E0: (0x7D437C, 0x5A05F0, 2404, (1435, 1436, 1436)),
    0x5A07F0: (0x7D43D0, 0x5A08C0, 2409, (1437, 1437, 1437)),
}

# SHA-256 of only the corresponding original null-terminated STR *text bytes*
# (without the final NUL), encoded CP1252. Prevent dataclass-replacement
# forgeries without embedding entire copyrighted original body messages.
ORIGINAL_606540_BODY_STRING_SHA256 = {
    1154: "9a9c8516492df22633b55fb492ffacdcb61572620dc914d58fe2be96be96594e",
    1156: "44b6d6710ae8997b598c721bd9d8d5d4f273fdc42f0d2354977f8cc2f097e864",
    1159: "b4b717b06bc963140da4bb6eb7e3bd2ceede4efee36dd3e3c140a189d4facc48",
    1161: "02be69b83cc6b12032c98127d883f1094bbac217a94352f2b7b6ab2cd463a32c",
    1163: "ad69ca57bb48970bfc3c29db65a497aeff61a8e342c13bc164f866941d837247",
    1165: "fdb5761d6a45f5a20d1e55a0eec29baeca215bc7c3c3ebd2bcc57828eb95c4a9",
    1167: "1fb982fa155330ee8d535a76ad4d129d959a48f46696a67aba542661987263c3",
    1169: "376c025c36a1cd3374fac73000f3325ff912a96419f3545c5d123a74a63433ac",
    1170: "94dfc694b8fdbf7d3592875bc4d8b903f77d8f77af8507b5d8e10fd79db2f608",
    1172: "ee7a78bebeecd7b2b47ca54438c5f6071a757eb2008364a549e110169e63373e",
    1432: "a0687c9440e6c2b14fa5c5e7222e3b4806ab59a88ee674ea023d95e56d6c16c8",
    1433: "701276d49578d6f0d12c2631daa7b1591db999bf0a46bd016d9af0d47b70708d",
    1434: "9b6994ca84fe612399757292a5fefe5b7fb221bbdf30449e05bba47041ca4f1c",
    1435: "d5fc59d0d3c0b7487cc5d07585281f7a96c4a560ec04267e96029e022e607e12",
    1436: "b9442522fdb1fd382b0c35d8ac3b4b1c8a7a085be33cb5e8a4ac750ede9afafa",
    1437: "b0ea51b6302231215099f7c64976def47b936db1ed3c0f6de5a1038a374a01da",
}


@dataclass(frozen=True)
class VerifiedOriginalEAMailLanguage:
    strings: EAStringTable
    index: EAStringIndex

    def original_606540_notice_body_template(
        self, due_receipt, *, native_variant: int
    ) -> str:
        """Read source-only 606540 +0x1C variant 0/1/2, not rendered mail.

        Native function dispatch branches on the explicit +0x1C argument.
        The program's choice of argument at the actual player screen, native
        string-token interpolation and registered-user delivery are unproven.
        """
        from original_native_606540_human_mail_route import (
            Original606540HumanDueReceipt,
        )
        if type(due_receipt) is not Original606540HumanDueReceipt:
            raise OriginalEAMailLanguageError(
                "Original 606540 source-qualified due receipt required"
            )
        if type(native_variant) is not int or native_variant not in (0, 1, 2):
            raise OriginalEAMailLanguageError(
                "Original 606540 body variant must be native selector 0, 1 or 2"
            )
        route = ORIGINAL_606540_BODY_ROUTES.get(due_receipt.original_constructor)
        if route is None:
            raise OriginalEAMailLanguageError(
                "Unqualified original 606540 body constructor"
            )
        vtable, callback, first_ordinal, string_ids = route
        ordinal = first_ordinal + native_variant
        string_id = string_ids[native_variant]
        if (due_receipt.original_concrete_notice_vtable != vtable
                or not 0x401000 <= callback < 0x7B86BD
                or not 0 <= ordinal < len(self.index.string_ids)
                or self.index.string_ids[ordinal] != string_id
                or not 0x877F38 <= 0x87AC28 - ordinal * 4 <= 0x87AC28
                or string_id not in ORIGINAL_606540_BODY_STRING_SHA256):
            raise OriginalEAMailLanguageError(
                "Original 606540 body vtable/language selector mismatch"
            )
        template = self.index.resolve(self.strings, ordinal)
        try:
            actual_hash = sha256(template.encode("cp1252")).hexdigest()
        except UnicodeEncodeError as exc:
            raise OriginalEAMailLanguageError(
                "Original 606540 body is not native CP1252"
            ) from exc
        if actual_hash != ORIGINAL_606540_BODY_STRING_SHA256[string_id]:
            raise OriginalEAMailLanguageError(
                "Original 606540 body source text changed"
            )
        return template

    def original_606540_notice_subject_template(self, due_receipt) -> str:
        """Read only source-proven +0x18 localized title for a 606540 notice.

        Requires a typed original 606540 constructor -> 7BD564 -> 413020
        *source projection* receipt. The resulting original title may still
        contain native PLAYERNAME interpolation. This method neither formats
        that token nor produces a delivered or visible user Inbox item.
        """
        from original_native_606540_human_mail_route import (
            Original606540HumanDueReceipt,
        )
        if type(due_receipt) is not Original606540HumanDueReceipt:
            raise OriginalEAMailLanguageError(
                "Original 606540 source-qualified due receipt required"
            )
        entry = ORIGINAL_606540_TITLE_ROUTES.get(due_receipt.original_constructor)
        if entry is None:
            raise OriginalEAMailLanguageError(
                "Unqualified original 606540 notice constructor"
            )
        vtable, tag, title_function, ordinal, string_id = entry
        if (due_receipt.original_concrete_notice_vtable != vtable
                or due_receipt.original_native_virtual0c_tag != tag
                or not 0 <= ordinal < len(self.index.string_ids)
                or self.index.string_ids[ordinal] != string_id
                or self.strings[string_id]
                != ORIGINAL_606540_TITLE_SOURCE_TEXTS[string_id]
                or not 0x401000 <= title_function < 0x7B86BD
                or (0x87AC28 - (4 * ordinal)) < 0x877F38):
            raise OriginalEAMailLanguageError(
                "Original 606540 vtable/language selector or resource mismatch"
            )
        return self.index.resolve(self.strings, ordinal)

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

    def original_player_asks_transfer_list_reason_phrase(self, native_reason: int) -> str:
        """Source 0x60FE40 branch for original transfer-request PHRASE token.

        Native reason must already have been assigned by the qualified
        first-preview path. Never draw RNG or substitute PLAYER/MANAGER here.
        """
        if type(native_reason) is not int or not 1 <= native_reason <= 7:
            raise OriginalEAMailLanguageError(
                "Unassigned or invalid original transfer-preview reason"
            )
        offset = native_reason - 1
        ordinal = ORIGINAL_TRANSFER_REASON_FIRST_IDX_ORDINAL + offset
        expected_id = ORIGINAL_TRANSFER_REASON_STRING_IDS[offset]
        expected_slot = ORIGINAL_TRANSFER_REASON_FIRST_SLOT_VA - 4 * offset
        if ((0x87AC28 - expected_slot) // 4 != ordinal
                or self.index.string_ids[ordinal] != expected_id):
            raise OriginalEAMailLanguageError(
                "Original transfer reason native language slot mismatch"
            )
        return self.index.resolve(self.strings, ordinal)

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
