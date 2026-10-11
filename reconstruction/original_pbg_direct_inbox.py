"""Original management PBg direct Inbox child ID1 source contract.

Canonical original PE SHA-256 833bf95e...b7cc3:
0x43092B..0x430957 constructs PBg+0x49C ID1;
0x431850 binds 0x943B10 back_3.444 40x95;
0x432690 / 0x4326D6 dispatches 0x482BF0(0x65) unless the
top-panel pointer already equals native PEAMail singleton 0x876758.
PMenu popup occlusion/disabled/animation remain unresolved; no implicit
screen text, status sprite, Win11 click acceptance, or record mutation.
"""

PBG_DIRECT_EAMAIL_ID = 1
PBG_DIRECT_EAMAIL_RECT = (558, 0, 40, 95)
PBG_DIRECT_EAMAIL_FACTORY_ID = 0x65


def original_pbg_direct_eamail_press(
    x: int,
    y: int,
    *,
    active_panel_class: str,
    pmenu_popup_active: bool,
) -> bool:
    """Bounded source-owned header child dispatch, not a guessed shortcut.

    Do not route through an open PMenu overlay; its click stack and
    occlusion remain a separate native acceptance boundary.
    """
    if type(x) is not int or type(y) is not int:
        raise ValueError("Original PBg press requires integer native pixels")
    if type(active_panel_class) is not str or type(pmenu_popup_active) is not bool:
        raise ValueError("Original PBg press requires current owner/stack state")
    if pmenu_popup_active or active_panel_class == "PEAMail":
        return False
    sx, sy, w, h = PBG_DIRECT_EAMAIL_RECT
    return sx <= x < sx + w and sy <= y < sy + h
