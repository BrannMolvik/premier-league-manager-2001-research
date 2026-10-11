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
Original 0x40DA70 uses the registered user's nonempty +0xD0 caption if
that club is owned by the user; otherwise it selects DBRClub+0x0C,
the original short-name pointer. The following builder requires its caller
to prove the selected-user registration and the caption's source status.
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


ORIGINAL_EAM_CLUB_CAPTION_GETTER_VA = 0x40DA70
ORIGINAL_EAM_CLUB_CAPTION_OVERRIDE_VA = 0x403600
ORIGINAL_EAM_USER_CLUB_MATCH_VA = 0x4037B0
ORIGINAL_EAM_USER_CLUB_FIND_VA = 0x413B40
ORIGINAL_EAM_USER_CLUB_CAPTION_OFFSET = 0xD0
ORIGINAL_EAM_CLUB_SHORT_NAME_OFFSET = 0x0C


def original_eam_player_positive_association_label(
    *,
    first_name: str,
    surname: str,
    verified_native_association_word: int,
    source_club_short_name: str,
    source_verified_user_caption: str | None,
    verified_original_club_suffix: str,
) -> str:
    """Native 0x5CE735 positive descriptor + 0x40DA70 club caption.

    Nonempty DBRUser+0xD0 caption takes priority only for the matching
    registered human's club. Otherwise native DBRClub+0x0C supplies the
    SHORT name, not the +0x08 full name. The caller must independently prove
    both original club lookup/one-user context and the original English
    0x9844D8 language suffix; None means override state is not known.
    """
    assoc = verified_native_association_word
    if type(assoc) is not int or not 0 <= assoc < (1 << 15):
        raise OriginalEAMPlayerNameSourceError(
            "Source-qualified native nonnegative descriptor club word is required"
        )
    if type(source_verified_user_caption) is not str:
        raise OriginalEAMPlayerNameSourceError(
            "Original registered-user club caption context is unresolved"
        )
    if source_verified_user_caption:
        caption = _source_cp1252(source_verified_user_caption, "user club caption")
    else:
        caption = _source_cp1252(source_club_short_name, "club short name")
    suffix = _source_cp1252(verified_original_club_suffix, "club suffix")
    if suffix.decode("cp1252") != "Football Club":
        raise OriginalEAMPlayerNameSourceError(
            "Original 0x9844D8 club suffix must come from verified English.str"
        )
    player = original_eam_player_initial_surname(first_name, surname)
    return ORIGINAL_EAM_PLAYER_HAS_ASSOCIATION_FORMAT % (
        player, caption.decode("cp1252"), suffix.decode("cp1252"),
    )
