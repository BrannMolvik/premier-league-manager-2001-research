"""Source-backed ownership for the FM2001 CRWD audio resource family.

The canonical executable directly selects one bank/card pair from the CRWD
directory and conditionally initializes CMIDI.BNK. This records only exact
resource identity and selection behavior; user-facing sound/music semantics,
sample mappings and playback timing remain unresolved.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14CrwdResourceOwnershipError(ValueError):
    pass


MAIN_AUDIO_INIT_VA = 0x6D0AC0
CMIDI_INIT_VA = 0x7229B0
CRWD_RESOURCE_LOADER_VA = 0x722A80
CRWD_PAIR_INIT_VA = 0x722AF0
CRWD_PATH_FORMAT_VA = 0x866268
RUNTIME_MODE_GLOBAL_VA = 0xAD62A0
ACTIVE_BANK_HANDLE_GLOBAL_VA = 0xA87850
ACTIVE_CARD_HANDLE_GLOBAL_VA = 0xA87854
ACTIVE_BANK_ID_GLOBAL_VA = 0xA87858


@dataclass(frozen=True)
class CrwdResource:
    filename: str
    size_bytes: int
    sha256: str
    string_va: int
    reference_va: int
    owner_init_va: int
    user_role_recovered: bool = False
    sample_mapping_recovered: bool = False
    playback_timing_recovered: bool = False
    music_semantics_recovered: bool = False

    def __post_init__(self) -> None:
        if not self.filename:
            raise Gate14CrwdResourceOwnershipError("CRWD filename must be non-empty")
        if type(self.size_bytes) is not int or self.size_bytes <= 0:
            raise Gate14CrwdResourceOwnershipError("CRWD resource size must be positive")
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)
        ):
            raise Gate14CrwdResourceOwnershipError(
                "CRWD resource SHA-256 must be lowercase hexadecimal"
            )
        if any(
            type(value) is not int
            for value in (self.string_va, self.reference_va, self.owner_init_va)
        ):
            raise Gate14CrwdResourceOwnershipError(
                "CRWD source addresses must be integers"
            )
        if (
            self.user_role_recovered
            or self.sample_mapping_recovered
            or self.playback_timing_recovered
            or self.music_semantics_recovered
        ):
            raise Gate14CrwdResourceOwnershipError(
                "CRWD ownership cannot promote unresolved audio semantics"
            )


CMIDI = CrwdResource(
    "CMIDI.BNK",
    446548,
    "5cd99c9a01039756fa9525a945ddb9a08fece0d31e85fcb7a8af7c5220680ad4",
    0x86625C,
    0x7229BE,
    CMIDI_INIT_VA,
)
CROWD_BANK = CrwdResource(
    "CROWD.BNK",
    72592,
    "d1e5268a1e221453e144f47803d9246ee49958584f205c2fe8acecc9bc8dcb59",
    0x866288,
    0x722B36,
    CRWD_PAIR_INIT_VA,
)
CROWD_CARD = CrwdResource(
    "CROWD.CRD",
    5480,
    "445c84cb54dd40b85617e970b1596e325074b54f2af345eae4227a3f9c43d705",
    0x86627C,
    0x722B45,
    CRWD_PAIR_INIT_VA,
)
TRAFF_BANK = CrwdResource(
    "traff.bnk",
    235952,
    "02bffe61944a3b1771756e2d7822fdb84dbf98bf815d010e4cb65c2c4136fc55",
    0x8662A0,
    0x722B20,
    CRWD_PAIR_INIT_VA,
)
TRAFF_CARD = CrwdResource(
    "TRAFF.CRD",
    1384,
    "dc6a630855b418053e08a637e85a9ec94b2a5b314f0796155de73d052ed1f5fc",
    0x866294,
    0x722B2F,
    CRWD_PAIR_INIT_VA,
)

CRWD_RESOURCES = (CMIDI, CROWD_BANK, CROWD_CARD, TRAFF_BANK, TRAFF_CARD)


@dataclass(frozen=True)
class CrwdModeSelection:
    runtime_mode: int
    bank: CrwdResource
    card: CrwdResource
    initializes_cmidi: bool
    exact_mode_semantics_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.runtime_mode) is not int:
            raise Gate14CrwdResourceOwnershipError("runtime mode must be integer")
        if self.bank not in (CROWD_BANK, TRAFF_BANK):
            raise Gate14CrwdResourceOwnershipError("CRWD mode requires known bank")
        if self.card not in (CROWD_CARD, TRAFF_CARD):
            raise Gate14CrwdResourceOwnershipError("CRWD mode requires known card")
        if self.exact_mode_semantics_recovered:
            raise Gate14CrwdResourceOwnershipError(
                "numeric CRWD mode cannot be given unrecovered user semantics"
            )


def crwd_selection_for_runtime_mode(runtime_mode: int) -> CrwdModeSelection:
    """Return the exact source branch selected by 0x722AF0.

    Only equality with 1 is source-significant here. The human-facing meaning
    of that mode value remains unrecovered.
    """
    if type(runtime_mode) is not int:
        raise Gate14CrwdResourceOwnershipError("runtime mode must be integer")
    if runtime_mode == 1:
        return CrwdModeSelection(runtime_mode, TRAFF_BANK, TRAFF_CARD, False)
    return CrwdModeSelection(runtime_mode, CROWD_BANK, CROWD_CARD, True)
