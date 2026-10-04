"""Source-closed partial ownership for FM2001 named audio banks.

Private tracing of the canonical executable closes exact loader slot assignment
for the four embedded named .bnk resources and two bounded playback consumers.

This contract deliberately separates:
* source-proven bank filename -> runtime slot identity;
* source-proven control/advice playback ownership;
* still-unresolved semantic roles for game00/playercalls and login/menu music.

A filename such as "menus.bnk" is not itself proof that the bank contains or
owns background menu music.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14AudioOwnershipError(ValueError):
    pass


@dataclass(frozen=True)
class Gate14NamedBank:
    slot: int
    filename: str
    string_va: int
    loader_call_va: int
    loaded_flag_va: int
    proven_consumer: str | None
    playback_semantics_recovered: bool

    def __post_init__(self) -> None:
        if type(self.slot) is not int or not 0 <= self.slot <= 3:
            raise Gate14AudioOwnershipError("named audio-bank slot must be 0..3")
        if not self.filename.endswith(".bnk"):
            raise Gate14AudioOwnershipError("named audio-bank filename must end in .bnk")
        for value in (self.string_va, self.loader_call_va, self.loaded_flag_va):
            if type(value) is not int or value <= 0:
                raise Gate14AudioOwnershipError(
                    "named audio-bank source addresses must be positive integers"
                )
        if self.proven_consumer is None and self.playback_semantics_recovered:
            raise Gate14AudioOwnershipError(
                "audio bank cannot recover playback semantics without a proven consumer"
            )
        if self.proven_consumer is not None and not self.proven_consumer:
            raise Gate14AudioOwnershipError("proven audio consumer must be non-empty")


AUDIO_BANK_LOADER_VA = 0x6D01F0
AUDIO_BANK_HANDLE_TABLE_VA = 0xA25988
AUDIO_BANK_RUNTIME_BYTE_TABLE_VA = 0xA2598C

MENUS_BANK = Gate14NamedBank(
    slot=0,
    filename="menus.bnk",
    string_va=0x8611F0,
    loader_call_va=0x6D01A4,
    loaded_flag_va=0xA259AC,
    proven_consumer="generic_control_audio_hooks_fixed_sample_family",
    playback_semantics_recovered=True,
)

GAME00_BANK = Gate14NamedBank(
    slot=1,
    filename="game00.bnk",
    string_va=0x8611E4,
    loader_call_va=0x6D01D9,
    loaded_flag_va=0xA259AC,
    proven_consumer=None,
    playback_semantics_recovered=False,
)

PLAYERCALLS_BANK = Gate14NamedBank(
    slot=2,
    filename="playercalls.bnk",
    string_va=0x861214,
    loader_call_va=0x6D0292,
    loaded_flag_va=0xA259A8,
    proven_consumer=None,
    playback_semantics_recovered=False,
)

ADVICE_BANK = Gate14NamedBank(
    slot=3,
    filename="Advice.bnk",
    string_va=0x861224,
    loader_call_va=0x6D0309,
    loaded_flag_va=0xA259B0,
    proven_consumer="formation_popup_success_feedback",
    playback_semantics_recovered=True,
)

NAMED_AUDIO_BANKS = (
    MENUS_BANK,
    GAME00_BANK,
    PLAYERCALLS_BANK,
    ADVICE_BANK,
)

# Slot-0 generic control-audio source chain.
AUDIO_HOOKS_TYPE_DESCRIPTOR_VA = 0x833BA8
ECONTROL_AUDIO_HOOKS_TYPE_DESCRIPTOR_VA = 0x833B80
AUDIO_HOOKS_VTABLE_VA = 0x7D73EC
CONTROL_AUDIO_MAPPING_DISPATCH_VA = 0x5DBFC0
CONTROL_AUDIO_SLOT0_PLAY_VA = 0x6CFF10

# The dispatcher maps source control/action state to fixed slot-0 sample IDs.
CONTROL_AUDIO_FIXED_SAMPLE_IDS = (
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
)

# Slot-3 source-owned formation popup path.
FORMATION_POPUP_AUDIO_CALLER_VA = 0x6CEBE0
FORMATION_POPUP_ADVICE_CALL_VA = 0x6CEC22
ADVICE_SLOT3_PLAY_VA = 0x6CFFA0
FORMATION_HOTKEY1_KEY_VA = 0x849E98
FORMATION_HOTKEY2_KEY_VA = 0x849E84
FORMATION_POPUP_TITLE_KEY_VA = 0x849EAC
RETURN_TO_EXIT_KEY_VA = 0x849E74

# Generalized dispatcher: mode 0 selects slot 1, mode 1 selects slot 2.
# This proves slot selection only, not human-readable game00/playercalls roles.
GENERAL_AUDIO_DISPATCH_VA = 0x6D0050
GENERAL_MODE0_SLOT = 1
GENERAL_MODE1_SLOT = 2


@dataclass(frozen=True)
class Gate14AudioOwnership:
    banks: tuple[Gate14NamedBank, ...] = NAMED_AUDIO_BANKS
    slot0_control_audio_recovered: bool = True
    slot3_formation_advice_recovered: bool = True
    slot1_game00_playback_role_recovered: bool = False
    slot2_playercalls_playback_role_recovered: bool = False
    login_menu_music_recovered: bool = False
    match_audio_event_bindings_recovered: bool = False
    audio_integration_complete: bool = False

    def __post_init__(self) -> None:
        if tuple(bank.slot for bank in self.banks) != (0, 1, 2, 3):
            raise Gate14AudioOwnershipError(
                "named audio-bank contract must retain slots 0..3 in source order"
            )
        if len({bank.filename for bank in self.banks}) != len(self.banks):
            raise Gate14AudioOwnershipError("named audio-bank filenames must be unique")
        if not self.slot0_control_audio_recovered or not self.slot3_formation_advice_recovered:
            raise Gate14AudioOwnershipError(
                "audio ownership contract cannot weaken source-closed consumers"
            )
        if (
            self.slot1_game00_playback_role_recovered
            or self.slot2_playercalls_playback_role_recovered
            or self.login_menu_music_recovered
            or self.match_audio_event_bindings_recovered
            or self.audio_integration_complete
        ):
            raise Gate14AudioOwnershipError(
                "audio ownership checkpoint cannot promote unresolved roles"
            )


def named_bank_for_slot(slot: int) -> Gate14NamedBank:
    if type(slot) is not int or not 0 <= slot < len(NAMED_AUDIO_BANKS):
        raise Gate14AudioOwnershipError("named audio-bank slot must be 0..3")
    return NAMED_AUDIO_BANKS[slot]
