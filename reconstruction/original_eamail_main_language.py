"""Original English.str/idx localized EAM row club suffix and date.

Native executable SHA-256 833bf95e...b7cc3. English.idx loader reads 2,714
uint16 indices in order (0x635F6D..0x64C7BF); 0x64E320 binds their STR
string pointers. Row native functions:
- descriptor-positive EAM 0x5CE73C uses global 0x9844D8 = ordinal 200;
- PMessageRow 0x471F3E uses global 0x981DA4 = ordinal 2709;
- 0x64D150 formats %D/%M/%Yf: decimal unpadded day, three-byte month
  abbreviation, full 1900+year year; native 0x64D140 month pointers
  at 0x84A030 select ordinal 125..136 for months January..December.

Only the source-backed English format is supported. No true original GUI
observation or player/club-name dynamic override is asserted.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from pathlib import Path

from ea_language_strings import EAStringIndex, EAStringTable, parse_language_pair


class OriginalEAMMainLanguageError(ValueError):
    """Original main-game English language bytes or native selector mismatch."""


ORIGINAL_MAIN_STR_FILE = "English.str"
ORIGINAL_MAIN_IDX_FILE = "English.idx"
ORIGINAL_MAIN_STR_SIZE = 369644
ORIGINAL_MAIN_IDX_SIZE = 5428
ORIGINAL_MAIN_STR_SHA256 = (
    "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601"
)
ORIGINAL_MAIN_IDX_SHA256 = (
    "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1"
)
ORIGINAL_MAIN_IDX_COUNT = 2714
ORIGINAL_MAIN_STR_COUNT = 21856
ORIGINAL_EAM_CLUB_SUFFIX_GLOBAL_VA = 0x9844D8
ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL = 200
ORIGINAL_EAM_CLUB_SUFFIX_STR_ID = 19781
ORIGINAL_EAM_DATE_GLOBAL_VA = 0x981DA4
ORIGINAL_EAM_DATE_IDX_ORDINAL = 2709
ORIGINAL_EAM_DATE_STR_ID = 21852
ORIGINAL_EAM_DATE_FORMAT = "%D/%M/%Yf"
ORIGINAL_EAM_MONTH_POINTER_TABLE_VA = 0x84A030
ORIGINAL_EAM_JANUARY_IDX_ORDINAL = 125
ORIGINAL_EAM_JANUARY_STR_ID = 19718


@dataclass(frozen=True)
class VerifiedOriginalMainEAMLanguage:
    strings: EAStringTable
    index: EAStringIndex

    def original_club_suffix(self) -> str:
        """0x5CE73C+0x9844D8 source fragment, not a guessed 'FC'."""
        if (self.index.string_ids[ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL]
                != ORIGINAL_EAM_CLUB_SUFFIX_STR_ID
                or self.index.resolve(
                    self.strings, ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL,
                ) != "Football Club"):
            raise OriginalEAMMainLanguageError("Native club suffix source mismatch")
        return self.index.resolve(
            self.strings, ORIGINAL_EAM_CLUB_SUFFIX_IDX_ORDINAL,
        )

    def original_mail_row_date(self, record_date: date) -> str:
        """0x471F3E/0x64D150 original English PMessageRow date column.

        Native %D reads calendar day at date+8 as decimal %i; %M without f
        copies three bytes of month name from 0x64D140; %Yf prints full year
        from native year-offset + 1900. This is NOT OS strftime %D or %M.
        """
        if type(record_date) is not date:
            raise OriginalEAMMainLanguageError("Source EAM row date is required")
        if (self.index.string_ids[ORIGINAL_EAM_DATE_IDX_ORDINAL]
                != ORIGINAL_EAM_DATE_STR_ID
                or self.index.resolve(
                    self.strings, ORIGINAL_EAM_DATE_IDX_ORDINAL,
                ) != ORIGINAL_EAM_DATE_FORMAT):
            raise OriginalEAMMainLanguageError("Native row date template source mismatch")
        ordinal = ORIGINAL_EAM_JANUARY_IDX_ORDINAL + record_date.month - 1
        sid = ORIGINAL_EAM_JANUARY_STR_ID + record_date.month - 1
        if self.index.string_ids[ordinal] != sid:
            raise OriginalEAMMainLanguageError("Native date month pointer source mismatch")
        month = self.index.resolve(self.strings, ordinal)
        encoded = month.encode("cp1252", errors="strict")
        if len(encoded) < 3:
            raise OriginalEAMMainLanguageError("Native month abbreviation is invalid")
        return f"{record_date.day}/{encoded[:3].decode('cp1252')}/{record_date.year}"


def load_verified_original_main_eam_language(
    original_source_root: str | Path,
) -> VerifiedOriginalMainEAMLanguage:
    """Read exact shipped main-game pair, with no synthetic fallbacks."""
    root = Path(original_source_root)
    chunks = []
    for name, length, digest in (
        (ORIGINAL_MAIN_STR_FILE, ORIGINAL_MAIN_STR_SIZE, ORIGINAL_MAIN_STR_SHA256),
        (ORIGINAL_MAIN_IDX_FILE, ORIGINAL_MAIN_IDX_SIZE, ORIGINAL_MAIN_IDX_SHA256),
    ):
        try:
            data = (root / name).read_bytes()
        except FileNotFoundError as exc:
            raise OriginalEAMMainLanguageError(
                f"Missing original English language file: {name}"
            ) from exc
        if len(data) != length or sha256(data).hexdigest() != digest:
            raise OriginalEAMMainLanguageError(
                f"Original English language source checksum mismatch: {name}"
            )
        chunks.append(data)
    strings, index = parse_language_pair(*chunks)
    if (len(strings.strings) != ORIGINAL_MAIN_STR_COUNT
            or len(index.string_ids) != ORIGINAL_MAIN_IDX_COUNT):
        raise OriginalEAMMainLanguageError(
            "Original English main-language string/index counts differ"
        )
    return VerifiedOriginalMainEAMLanguage(strings, index)
