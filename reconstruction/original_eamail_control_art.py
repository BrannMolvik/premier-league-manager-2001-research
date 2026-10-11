"""Authentic FM2001 EAMail source control art, no substitute screens.

The original PMessageRow 0x46E680 and EAMail sources include native
read/unread icon, toggle, preview and reply resources. These exact 14 source
assets were independently retrieved from the authorized original extracted
disc folder, verified by size, SHA-256 and original 8-byte EA444 geometry.

This does NOT infer icon status/read-bit semantics, pixel composition,
font, actions, modal return, ordinary PBg/PMenu entry or input capture.
The four native 532x18 text-grid states are separately pinned by
original_eamail_source_contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import EA444FormatError, parse_ea444_header


class OriginalEAMailArtSourceError(ValueError):
    """Missing, altered or non-native original EAMail art source."""


ORIGINAL_EAMAIL_ART_FOLDER = "FM2001_Art/Generic/EAMail"


@dataclass(frozen=True)
class OriginalEAMailArtSpec:
    name: str
    byte_size: int
    sha256: str
    dimensions: tuple[int, int]


ORIGINAL_EAMAIL_CONTROL_ART = (
    OriginalEAMailArtSpec("del_mail_button.444", 2652, "6caf5c7692cb6202aaac478ee043969416db3806bcccc724f2effcb4f6b61962", (38, 84)),
    OriginalEAMailArtSpec("mail_reply_popup.444", 56548, "937a126755d7cf656f020c808569a0e714094f26497718dcdeb2eab1d1e530a4", (710, 420)),
    OriginalEAMailArtSpec("mail_tog.444", 4768, "47159969da910dff5d95a3d80bcb3b753c41a45447c5c85f04a3985a71fe0a14", (22, 80)),
    OriginalEAMailArtSpec("next_mail_button.444", 3064, "8816dc0564958c1d64f222397ae6070f22f8246da620ffdcca27508f95215edc", (18, 84)),
    OriginalEAMailArtSpec("prev_mail_button.444", 3052, "b2011bd9db479aa239a0424254af5729fd21ad75cb5b6ddc9ff98e01efceab95", (18, 84)),
    OriginalEAMailArtSpec("preview_panel.444", 12648, "3ffacba2278a780fbcd38411aadf03694e0df4142ecdd2b9ae1638f8792adc46", (532, 187)),
    OriginalEAMailArtSpec("preview_panel_disabled.444", 13276, "5065ea4a66b5a5bde44ca2d8405d55230ea4f67ac31ec31f4931d54ea7cf9196", (532, 187)),
    OriginalEAMailArtSpec("read_mail_icon.444", 992, "dcabbe98342c66bf0cc3f073a7816aff6b242348fcc116af1ebb7a915ee86c21", (18, 12)),
    OriginalEAMailArtSpec("recieved_tog.444", 2592, "f9fc8fb1aadef25407544d7eefc1a310c8a3fc2a58bb721f30dcb1ef0fd8eb36", (73, 60)),
    OriginalEAMailArtSpec("send_mail_button.444", 2748, "e2076aedfe53d9596d746a8118839492ccaf929baa7cec251f3b03089fbe5a2a", (46, 84)),
    OriginalEAMailArtSpec("subject_tog.444", 8240, "b69e80046b18dd60fb79635625ba6638cef08befbacfcaba5505357671c73c10", (217, 80)),
    OriginalEAMailArtSpec("unread_mail_icon.444", 1152, "0535dbf3489d4dad1bbf7c1a6753ddd3a5adb046ced037bf01183e43d16f7fc6", (18, 12)),
    OriginalEAMailArtSpec("urgent_icon.444", 184, "ad8aa216962296002af3efd27373388ce8d50c5bd13b295bce7cdf0fdaa1cc06", (8, 16)),
    OriginalEAMailArtSpec("urgent_tog.444", 2120, "9b2bc59d7dd097ea837d9f66adb45ad4715900b069df2d79363361db5c0d1ff6", (12, 80)),
)


def validate_original_eamail_control_art(
    original_source_root: Path | str,
) -> tuple[OriginalEAMailArtSpec, ...]:
    """Reject any missing/corrupted native 444, rather than invent replacements."""
    root = Path(original_source_root) / ORIGINAL_EAMAIL_ART_FOLDER
    for spec in ORIGINAL_EAMAIL_CONTROL_ART:
        path = root / spec.name
        try:
            raw = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalEAMailArtSourceError(
                "Missing original Inbox resource: " + spec.name
            ) from exc
        if len(raw) != spec.byte_size or sha256(raw).hexdigest() != spec.sha256:
            raise OriginalEAMailArtSourceError(
                "Original Inbox resource bytes differ: " + spec.name
            )
        try:
            header = parse_ea444_header(raw)
        except EA444FormatError as exc:
            raise OriginalEAMailArtSourceError(
                "Original Inbox graphic header invalid: " + spec.name
            ) from exc
        if (header.width, header.height) != spec.dimensions:
            raise OriginalEAMailArtSourceError(
                "Original Inbox resource dimensions differ: " + spec.name
            )
    return ORIGINAL_EAMAIL_CONTROL_ART
