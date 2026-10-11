"""Original FM2001 EAM player-name and no-association typed label.

Authenticated original PE SHA-256 833bf95e...b7cc3: native 0x417AE0
formats row-player with first-initial/surname via literal "%c. %s" at
0x818EB0 (third parameter NULL at 0x5CE71C), or copies the surname
verbatim if original first-name byte is 0x2D ('-'). This original
player reference is then enclosed in native inline-color text markup
at 0x5CE784 using "<T+P>%s<T->" (literal 0x83330C) ONLY when the
source descriptor association field +0x08, captured from
DBRPlayer+0x72 at 0x5CE68D, is signed-negative.

When that association >=0, the original at 0x5CE73C invokes a
distinct original club/association presentation 0x40DA70 and formats
"<T+P>%s<T-> @ <T+C>%s %s<T->" (literal 0x833318).
That original club owner and two string fragments are NOT inferred here.
"""
from __future__ import annotations


class OriginalEAMPlayerNameSourceError(ValueError):
    """No original-game source proof for the requested player text branch."""


ORIGINAL_EAM_PLAYER_NAME_VA = 0x417AE0
ORIGINAL_EAM_PLAYER_NAME_INITIAL_SURNAME_FORMAT_VA = 0x818EB0
ORIGINAL_EAM_PLAYER_NAME_INITIAL_SURNAME_FORMAT = "%c. %s"
ORIGINAL_EAM_PLAYER_DESCRIPTOR_RESOLVE_VA = 0x5CE6A0
ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT_VA = 0x83330C
ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT = "<T+P>%s<T->"
ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT_VA = 0x833318
ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT = "<T+P>%s<T-> @ <T+C>%s %s<T->"
ORIGINAL_EAM_PLAYER_ASSOCIATION_RECORD_OFFSET = 0x72


def _source_cp1252(value: str, label: str) -> bytes:
    if type(value) is not str or not value:
        raise OriginalEAMPlayerNameSourceError(
            "Source original " + label + " must be a nonempty name"
        )
    try:
        data = value.encode("cp1252", errors="strict")
    except UnicodeEncodeError as exc:
        raise OriginalEAMPlayerNameSourceError(
            "Source original " + label + " is not CP1252"
        ) from exc
    if b"\x00" in data:
        raise OriginalEAMPlayerNameSourceError(
            "Source original " + label + " contains native C terminator"
        )
    return data


def original_eam_player_initial_surname(first_name: str, surname: str) -> str:
    """Exact native 0x417AE0(… arg3=0) CP1252 player label.

    This uses the exact *first source byte* rather than Unicode grapheme
    slicing. A leading '-' source first-name causes original code to copy
    the actual surname verbatim (the football database's special-name case).
    Unlike modern display formatting, do not strip or title-case the name.
    """
    first = _source_cp1252(first_name, "first name")
    last = _source_cp1252(surname, "surname")
    if first[0] == 0x2D:
        return last.decode("cp1252")
    return (bytes((first[0],)) + b". " + last).decode("cp1252")


def original_eam_player_no_association_label(
    *,
    first_name: str,
    surname: str,
    verified_native_association_word: int,
) -> str:
    """Source exact kind2/descriptor-negative original row markup.

    Requires native DBRPlayer+0x72 *signed-word* provenance. The port's
    current club_id or loan_club_id alone does not prove that native value.
    Positive association refuses unsupported original 0x40DA70 text.
    """
    assoc = verified_native_association_word
    if type(assoc) is not int or not -(1 << 15) <= assoc < (1 << 15):
        raise OriginalEAMPlayerNameSourceError(
            "Original DBRPlayer+0x72 signed-word association is required"
        )
    if assoc >= 0:
        raise OriginalEAMPlayerNameSourceError(
            "Native player association requires original 0x40DA70 and club text"
        )
    name = original_eam_player_initial_surname(first_name, surname)
    return ORIGINAL_EAM_PLAYER_NO_ASSOCIATION_FORMAT % name
