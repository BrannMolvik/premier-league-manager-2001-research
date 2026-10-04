"""Source-backed ownership for FM2001 speech stream/index resources.

The canonical executable directly constructs these speech resource paths during
audio initialization. This module binds only resource identity and owner call
sites. Phrase selection, event mapping, playback timing and commentary
semantics remain unresolved.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14SpeechResourceOwnershipError(ValueError):
    pass


SPEECH_INIT_VA = 0x723AD0
SPEECH_PATH_BUILDER_VA = 0x723E20
TEAM_SPEECH_INIT_VA = 0x723E70
PLAYER_STITCHED_SPEECH_INIT_VA = 0x724080
MAIN_AUDIO_INIT_VA = 0x6D0AC0
SPEECH_PATH_FORMAT_VA = 0x8663F0


@dataclass(frozen=True)
class SpeechResourceOwnership:
    path: str
    size_bytes: int
    sha256: str
    string_va: int
    reference_va: int
    owner_init_va: int
    phrase_mapping_recovered: bool = False
    event_binding_recovered: bool = False
    playback_timing_recovered: bool = False
    commentary_ready: bool = False

    def __post_init__(self) -> None:
        if not self.path.startswith("Data/Audio/Speech/"):
            raise Gate14SpeechResourceOwnershipError(
                "speech resource must remain under Data/Audio/Speech"
            )
        if type(self.size_bytes) is not int or self.size_bytes <= 0:
            raise Gate14SpeechResourceOwnershipError(
                "speech resource size must be positive"
            )
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)
        ):
            raise Gate14SpeechResourceOwnershipError(
                "speech resource SHA-256 must be lowercase hexadecimal"
            )
        if any(
            type(value) is not int
            for value in (self.string_va, self.reference_va, self.owner_init_va)
        ):
            raise Gate14SpeechResourceOwnershipError(
                "speech resource source addresses must be integers"
            )
        if (
            self.phrase_mapping_recovered
            or self.event_binding_recovered
            or self.playback_timing_recovered
            or self.commentary_ready
        ):
            raise Gate14SpeechResourceOwnershipError(
                "resource ownership cannot promote unresolved speech semantics"
            )


SPEECH_RESOURCES = (
    SpeechResourceOwnership(
        "Data/Audio/Speech/NewSpeech.inf",
        26879,
        "b0d0be607f669051a2b4ee884578f8da277f9cd912baf72849c56cec4ee89a25",
        0x86638C,
        0x723CAF,
        SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/NewSpeech.str",
        86879932,
        "fd0d511c1482080e49cd49b2baa7396ea53e2866bacebfd0dac6515ab6211c1e",
        0x8663AC,
        0x723C84,
        SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Stitched.str",
        500960,
        "c3fd52af55b6abf1270fb9cd0cd496702bf3c1068ca6274080e64813c98c0c00",
        0x86639C,
        0x723C93,
        SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Teams.off",
        2244,
        "a16c7df782db703e5c3d284bdbf1ff35653f65bc5e2b730e8a17518e7828f54f",
        0x866408,
        0x723EC5,
        TEAM_SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Teams.str",
        1812912,
        "57e04f874806174b6af16ae2dcbf586cf68807eb71707ab5dc01010b6246a18a",
        0x866414,
        0x723EB0,
        TEAM_SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Stitched.off",
        1036,
        "37954be2c825b712215959356ec0940946406e47c30c5aca395cdcf59106a96e",
        0x866420,
        0x7241F2,
        PLAYER_STITCHED_SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Players.str",
        11392368,
        "bd1fabdbebe7aae37fe8878f5a794a069cf6954064a4a450df454b3d9e6ae6c1",
        0x866430,
        0x724100,
        PLAYER_STITCHED_SPEECH_INIT_VA,
    ),
    SpeechResourceOwnership(
        "Data/Audio/Speech/Players.off",
        25692,
        "228f53d810e998e8bdb02c610905e28c80780e920ef677635591d9375a728b65",
        0x86643C,
        0x7240C8,
        PLAYER_STITCHED_SPEECH_INIT_VA,
    ),
)


def speech_resource(path: str) -> SpeechResourceOwnership:
    if not isinstance(path, str):
        raise Gate14SpeechResourceOwnershipError("speech resource path must be text")
    wanted = path.replace("\\", "/").casefold()
    for item in SPEECH_RESOURCES:
        if item.path.casefold() == wanted:
            return item
    raise Gate14SpeechResourceOwnershipError("unknown source-backed speech resource")
