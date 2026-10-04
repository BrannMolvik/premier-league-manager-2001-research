"""Source-backed FM2001 chant resource catalog boundary.

The private source pass inventories every bank under Data/Audio/Chants and
binds the executable's CHANT.eam loader plus dynamic naming formats. The exact
bank inventory is summarized by a deterministic digest over sorted
(path,size_bytes,sha256) records. This does not decode MIDx sequencing, map a
bank to a club/event, or recover playback timing.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ChantCatalogError(ValueError):
    pass


CHANT_INIT_VA = 0x722D80
CHANT_CONTROL_PATH_VA = 0x866314
CHANT_DIRECTORY_SUFFIX_VA = 0x866300
CHANT_INTERNAL_NAME_VA = 0x866338
CHANT_PATH_BUFFER_VA = 0xA879BC
CHANT_CONTROL_HANDLE_VA = 0xA878EC
CHANT_READY_GLOBAL_VA = 0xA878D0

ACTIVE_HOME_CLUB_GLOBAL_VA = 0xAD6060
ACTIVE_AWAY_CLUB_GLOBAL_VA = 0xAD6174
CLUB_SOURCE_ID_OFFSET = 0x32
CHANT_PAIR_SELECTION_VA = 0x722F00
CHANT_DYNAMIC_LOAD_VA = 0x723010

CL_FORMAT_VA = 0x866360
CL_FORMAT = "cl%06.6d"
C0_FORMAT_VA = 0x86634C
C0_FORMAT = "c0%4.4d"

CONTROL_PATH = "Data/Audio/Chants/CHANT.eam"
CONTROL_SIZE_BYTES = 704
CONTROL_SHA256 = "b2b26a6a8a7c2d904df4868ee8454169ef49dbd69b07fa22d926ec11aafafbee"
CONTROL_MAGIC = b"MIDx"

BANK_COUNT = 56
BANK_TOTAL_BYTES = 2_523_996
# SHA-256 of JSON-serialized sorted records, each containing exact
# path, size_bytes and file SHA-256 from the authorized source disc.
BANK_CATALOG_SHA256 = "b81f2f45c033d8da53f5a27696f07a70662f90fd277f51f5a3f3b1920c98c264"


@dataclass(frozen=True)
class ChantCatalogBoundary:
    control_path: str = CONTROL_PATH
    control_size_bytes: int = CONTROL_SIZE_BYTES
    control_sha256: str = CONTROL_SHA256
    control_magic: bytes = CONTROL_MAGIC
    bank_count: int = BANK_COUNT
    bank_total_bytes: int = BANK_TOTAL_BYTES
    bank_catalog_sha256: str = BANK_CATALOG_SHA256
    control_sequence_decoded: bool = False
    bank_to_club_mapping_recovered: bool = False
    event_binding_recovered: bool = False
    playback_timing_recovered: bool = False

    def __post_init__(self) -> None:
        if self.control_path != CONTROL_PATH:
            raise Gate14ChantCatalogError("CHANT control path drift")
        if self.control_size_bytes != CONTROL_SIZE_BYTES:
            raise Gate14ChantCatalogError("CHANT control byte-size drift")
        for digest in (self.control_sha256, self.bank_catalog_sha256):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(ch not in "0123456789abcdef" for ch in digest)
            ):
                raise Gate14ChantCatalogError("chant hashes must be lowercase SHA-256")
        if self.control_magic != b"MIDx":
            raise Gate14ChantCatalogError("CHANT.eam magic must remain MIDx")
        if self.bank_count != BANK_COUNT or self.bank_total_bytes != BANK_TOTAL_BYTES:
            raise Gate14ChantCatalogError("chant bank inventory summary drift")
        if (
            self.control_sequence_decoded
            or self.bank_to_club_mapping_recovered
            or self.event_binding_recovered
            or self.playback_timing_recovered
        ):
            raise Gate14ChantCatalogError(
                "chant catalog cannot promote unrecovered sequencing semantics"
            )


SOURCE_BOUNDARY = ChantCatalogBoundary()


def dynamic_chant_inputs() -> dict:
    """Return only the source-proven inputs to the unresolved naming logic."""
    return {
        "home_club_global_va": ACTIVE_HOME_CLUB_GLOBAL_VA,
        "away_club_global_va": ACTIVE_AWAY_CLUB_GLOBAL_VA,
        "club_source_id_offset": CLUB_SOURCE_ID_OFFSET,
        "cl_format": CL_FORMAT,
        "c0_format": C0_FORMAT,
        "pair_selection_va": CHANT_PAIR_SELECTION_VA,
        "dynamic_load_va": CHANT_DYNAMIC_LOAD_VA,
        "bank_to_club_mapping_recovered": False,
    }
