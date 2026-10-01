"""Fail-closed contract for the four executable-correlated Squad resources.

The names alone are not ownership evidence.  The canonical executable binds
each exact path to a resource handle and its RTTI-backed presentation methods
establish the owners recorded below.  In particular, ``blue_toggle.444`` is a
shared control resource and is not evidence of PSquadScreen ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from ea_language_strings import parse_language_pair


@dataclass(frozen=True)
class OriginalSquadResource:
    source_path: str
    sha256: str
    size: tuple[int, int]
    path_literal_va: int
    raw_handle_va: int
    wrapper_va: int
    native_owners: tuple[str, ...]


SQUAD_BUTTON_ORIGINS = ((37, 92), (113, 92), (189, 92))
SQUAD_SCREEN_CLASS = "PSquadScreen"
SQUAD_SCREEN_TYPE_DESCRIPTOR_VA = 0x819D48
SQUAD_SCREEN_VFTABLE_VA = 0x7C5CA4
SQUAD_SCREEN_SETUP_VA = 0x4B5720


@dataclass(frozen=True)
class OriginalSquadButton:
    control_id: int
    object_offset: int
    label_global_va: int
    language_index: int
    original_text: str
    origin: tuple[int, int]


# PSquadScreen::0x4B5720 registers these controls through vtable slot +8
# (0x64F3C0), which stores the numeric ID and owner. The language loader's
# sequential 16-bit reads bind English.idx entries 2490..2492 to the globals.
# The first control receives a distinct setup flag, but its semantic name and
# all atlas-frame meanings remain deliberately unresolved.
SQUAD_BUTTONS = (
    OriginalSquadButton(3, 0x37A4, 0x982110, 2490, "1ST & RES", (37, 92)),
    OriginalSquadButton(4, 0x37F8, 0x98210C, 2491, "1ST FORM", (113, 92)),
    OriginalSquadButton(5, 0x384C, 0x982108, 2492, "RES. FORM", (189, 92)),
)

SQUAD_RESOURCES = (
    OriginalSquadResource(
        "FM2001_Art/Coaching/squad/blue_toggle.444",
        "3fe515f5a4a2d798a8f62917a45047b274e08bd3e68147a4fe0e25dfbd1d3343",
        (22, 17),
        0x83827C,
        0x943070,
        0x943050,
        ("PFormation2k", "PSCFTitle", "PTraining", "PYouthTeam"),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_bars.444",
        "c0ba37cc991e5449830af3e550f14dc7d9444cc545e91fa7936dc38508c6110b",
        (81, 64),
        0x8394B8,
        0x941750,
        0x941730,
        ("FormationText",),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_but_anim.444",
        "6a5180d9212fe50418537fa181c44ba075bc0317c5bb55aed8b9c6a9e0fc0632",
        (73, 575),
        0x83943C,
        0x9417D0,
        0x9417B0,
        (SQUAD_SCREEN_CLASS,),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_form_anim.444",
        "e4bcc6981cc99fde44b093696791a05f91100752559b0b2f12dc0c0177392828",
        (23, 368),
        0x839478,
        0x941790,
        0x941770,
        ("FormationText",),
    ),
)


class OriginalSquadResourceError(ValueError):
    pass


def validate_imported_original_squad_resources(
    source_root: Path,
) -> tuple[OriginalSquadResource, ...]:
    """Require the four exact imported bytes and their native header geometry."""
    root = Path(source_root)
    for resource in SQUAD_RESOURCES:
        data = (root / resource.source_path).read_bytes()
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalSquadResourceError(
                f"Original Squad resource checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalSquadResourceError(
                f"Original Squad resource geometry mismatch: {resource.source_path}"
            )
    return SQUAD_RESOURCES


def validate_original_squad_button_labels(
    english_str: Path, english_idx: Path
) -> tuple[OriginalSquadButton, ...]:
    """Resolve the three executable-bound labels from the original language pair."""
    strings, index = parse_language_pair(
        Path(english_str).read_bytes(), Path(english_idx).read_bytes()
    )
    for button in SQUAD_BUTTONS:
        if index.resolve(strings, button.language_index) != button.original_text:
            raise OriginalSquadResourceError(
                f"Original Squad label mismatch at English.idx {button.language_index}"
            )
    return SQUAD_BUTTONS
