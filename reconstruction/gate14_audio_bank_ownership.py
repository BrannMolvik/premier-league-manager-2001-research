"""Source-backed FM2001 Gate-14 audio-bank ownership boundaries.

This module records only executable-proven bank loading and playback routing.
It deliberately does not infer music, commentary, crowd, UI meaning, or exact
sample names from bank filenames.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14AudioBankOwnershipError(ValueError):
    pass


BANK_LOADER_VA = 0x6D01F0
AUDIO_INIT_MENUS_GAME_VA = 0x6D0160
PLAYER_CALLS_LOADER_VA = 0x6D0250
ADVICE_LOADER_VA = 0x6D02F0
MAIN_AUDIO_BANK_INIT_VA = 0x6D0AC0

MENUS_PLAYBACK_VA = 0x6CFF10
ADVICE_PLAYBACK_VA = 0x6CFFA0
GENERIC_SFX_CALLBACK_VA = 0x6D0050
GENERIC_SFX_WRAPPER_VA = 0x6D0030
GENERIC_AUDIO_CALLBACK_INSTALLER_VA = 0x6D0480
GENERIC_AUDIO_CALLBACK_REGISTRATION_VA = 0x7255A0

AUDIO_HOOKS_VTABLE_VA = 0x7D73EC
AUDIO_HOOKS_DISPATCH_VA = 0x5DBFC0
AUDIO_HOOKS_RTTI = ".?AVAudioHooks@@"

BANK_HANDLE_BASE_VA = 0xA25988
BANK_ID_BASE_VA = 0xA2598C
BANK_SLOT_STRIDE = 8


@dataclass(frozen=True)
class AudioBankOwnership:
    slot: int
    filename: str
    string_va: int
    loader_owner_va: int
    playback_path: str
    playback_va: int | None
    role_semantics_recovered: bool = False
    exact_sample_semantics_recovered: bool = False
    music_semantics_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.slot) is not int or not 0 <= self.slot <= 3:
            raise Gate14AudioBankOwnershipError("audio bank slot must be 0..3")
        if not self.filename.endswith(".bnk"):
            raise Gate14AudioBankOwnershipError("audio bank filename must end in .bnk")
        if type(self.string_va) is not int or type(self.loader_owner_va) is not int:
            raise Gate14AudioBankOwnershipError("audio bank addresses must be integers")
        if not self.playback_path:
            raise Gate14AudioBankOwnershipError("audio bank playback path must be named")
        if self.playback_va is not None and type(self.playback_va) is not int:
            raise Gate14AudioBankOwnershipError("audio bank playback VA must be integer or None")
        if (
            self.role_semantics_recovered
            or self.exact_sample_semantics_recovered
            or self.music_semantics_recovered
        ):
            raise Gate14AudioBankOwnershipError(
                "bank ownership cannot promote unrecovered audio semantics"
            )

    @property
    def handle_global_va(self) -> int:
        return BANK_HANDLE_BASE_VA + self.slot * BANK_SLOT_STRIDE

    @property
    def bank_id_global_va(self) -> int:
        return BANK_ID_BASE_VA + self.slot * BANK_SLOT_STRIDE


BANKS = (
    AudioBankOwnership(
        slot=0,
        filename="menus.bnk",
        string_va=0x8611F0,
        loader_owner_va=AUDIO_INIT_MENUS_GAME_VA,
        playback_path="AudioHooks event/sample dispatcher",
        playback_va=MENUS_PLAYBACK_VA,
    ),
    AudioBankOwnership(
        slot=1,
        filename="game00.bnk",
        string_va=0x8611E4,
        loader_owner_va=AUDIO_INIT_MENUS_GAME_VA,
        playback_path="generic runtime SFX callback type=0",
        playback_va=GENERIC_SFX_CALLBACK_VA,
    ),
    AudioBankOwnership(
        slot=2,
        filename="playercalls.bnk",
        string_va=0x861214,
        loader_owner_va=PLAYER_CALLS_LOADER_VA,
        playback_path="generic runtime SFX callback type=1",
        playback_va=GENERIC_SFX_CALLBACK_VA,
    ),
    AudioBankOwnership(
        slot=3,
        filename="Advice.bnk",
        string_va=0x861224,
        loader_owner_va=ADVICE_LOADER_VA,
        playback_path="direct Advice-bank playback helper",
        playback_va=ADVICE_PLAYBACK_VA,
    ),
)


def bank_for_slot(slot: int) -> AudioBankOwnership:
    if type(slot) is not int:
        raise Gate14AudioBankOwnershipError("audio bank slot must be integer")
    for bank in BANKS:
        if bank.slot == slot:
            return bank
    raise Gate14AudioBankOwnershipError("unknown source-backed audio bank slot")


def generic_sfx_bank_for_type(type_byte: int) -> AudioBankOwnership:
    """Resolve only the two source-proven generic callback selectors.

    The generic callback at 0x6D0050 chooses slot 1 when type byte is zero and
    slot 2 when type byte is one. Other values use a caller-supplied slot and
    therefore remain outside this fixed mapping.
    """
    if type(type_byte) is not int or not 0 <= type_byte <= 0xFF:
        raise Gate14AudioBankOwnershipError("SFX type byte must be uint8")
    if type_byte == 0:
        return bank_for_slot(1)
    if type_byte == 1:
        return bank_for_slot(2)
    raise Gate14AudioBankOwnershipError(
        "generic SFX type uses caller-supplied slot; fixed ownership unresolved"
    )


def audio_hooks_bank() -> AudioBankOwnership:
    return bank_for_slot(0)


def advice_bank() -> AudioBankOwnership:
    return bank_for_slot(3)
