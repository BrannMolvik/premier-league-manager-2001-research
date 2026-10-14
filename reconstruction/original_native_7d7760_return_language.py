"""Source-authenticated original 5D7B40 injury RECOVERY message templates.

Exact original EnglishEAM STR/IDX (sha98387ef6... and bd0e2b80...).
Native virtual+0x18 localized caption and +0x1C variant 0/1/2 are
NOT the original 606540 injury-onset family. No interpolation, Inbox
recipient append, player-visible message, original native process run.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from original_eamail_language import VerifiedOriginalEAMailLanguage
from original_native_7d7760_human_return import (
    ORIGINAL_RECOVERY_NOTICE_ROUTES, Original7D7760HumanReturnSourceReceipt,
)


class OriginalRecoveryNoticeLanguageError(ValueError):
    pass


# SHA256(original CP1252 non-NUL source STR body), not duplicated copyrighted
# entire full original language strings. Companion original file pair must
# pass VerifiedOriginalEAMailLanguage loader's complete source SHA validation.
ORIGINAL_RECOVERY_BODY_SOURCE_SHA256 = {
    1408: "cb2a833e163a28f95d614fcd8d65a565b9b7ca12d753cd60f19db2fd4d09fdb5",
    1409: "2f77f2fdfa5722e1dcc9ab5bb8695aff77330e5cb1b0aca8b56e70d75553ad09",
    1411: "7aa7f32eed8f5ee439e75094fd6528ba29bc0df7ad8549c8603720f5cf8955f2",
    1413: "52f4dc3bd9b3fcf0ab6656108a145c444ab97857d01e17481583a7f95e80e708",
    1415: "3ddc3d9129db773ec4d1d83739db3d02fb4faa5ff95f3a3694b47a71bd0cd38c",
    1417: "a6ae3653f909df7d62a0442533c7b48040eae1116c340d04b6dab0c96a56a27e",
    1419: "3bdad2c16215a573b66eedd8eea20bff60b87154f29e7eed357be3ef4cfff73e",
    1421: "55b6598de9741b73512f09d15c4ff0dc1e7d22cf342e136744323a965a35f7b5",
    1423: "c6e31c4f6c514bab40127a6bc451b21cc535ecdde6cea923098e464becf91ef0",
    1425: "f37498f1a89caaabc300874de13dac76ad59ac85943b269927aa26ecb1e44aa6",
    1427: "1c3ce7b387c60f4993b5365b11e803b260bf3d6e2bf8e24b4047ca508c68fcce",
    1429: "762b8fd9f0f38ba30fefc1254010a85832efc62bbff026e042dfc76e69d5b907",
    1431: "12309bca8d10ae19863922a6b6b4bbf17933479ff82d1774cdc83b53c27c542c",
}
ORIGINAL_RECOVERY_TITLE_TEXT = "{PLAYERNAME:1} recovery"
ORIGINAL_RECOVERY_TITLE_STR_ID = 1407
ORIGINAL_RECOVERY_TITLE_SHA256 = (
    "aa4507b51d23a9ab3e87c2aec3af3158a17301f2b1945f4daf058c1ecd520c6d"
)


@dataclass(frozen=True)
class OriginalRecoveryUnexpandedNoticeTemplates:
    native_family: int
    native_status: int
    source_variant: int
    original_title_template: str
    original_body_template: str
    original_rendered_or_delivered: bool = False


def source_original_7d7760_recovery_templates(
    receipt: Original7D7760HumanReturnSourceReceipt,
    language: VerifiedOriginalEAMailLanguage,
    *,
    native_body_variant: int,
) -> OriginalRecoveryUnexpandedNoticeTemplates:
    """Read exactly the selected original STR messages, without GUI tokens."""
    if type(receipt) is not Original7D7760HumanReturnSourceReceipt:
        raise OriginalRecoveryNoticeLanguageError("Qualified original human due source receipt required")
    if (not receipt.original_registered_human
            or receipt.original_947aa8_human_event_insert_executed
            or receipt.original_user_inbox_delivered
            or receipt.live_game_state_updated
            or type(receipt.original_selected_family) is not int
            or receipt.original_selected_family not in ORIGINAL_RECOVERY_NOTICE_ROUTES
            or type(receipt.original_event_status) is not int
            or receipt.original_event_status not in range(4)):
        raise OriginalRecoveryNoticeLanguageError("Only source-qualified human recovery selection supported")
    if type(language) is not VerifiedOriginalEAMailLanguage:
        raise OriginalRecoveryNoticeLanguageError("Exact original EnglishEAM source pair required")
    if type(native_body_variant) is not int or native_body_variant not in (0,1,2):
        raise OriginalRecoveryNoticeLanguageError("Native +1C body selector 0/1/2 required")
    route=ORIGINAL_RECOVERY_NOTICE_ROUTES[receipt.original_selected_family][
        receipt.original_event_status]
    if (receipt.original_selected_constructor_if_human != route[0]
            or receipt.original_final_notice_vtable_if_human != route[1]
            or receipt.original_notice_title_callback_if_human != route[2]
            or receipt.original_notice_body_callback_if_human != route[3]
            or receipt.original_eamail_title_idx_if_human != route[4]
            or receipt.original_eamail_body_ids_if_human != route[5]):
        raise OriginalRecoveryNoticeLanguageError("Original return notice constructor/callback owner changed")
    idx=route[4]
    body_id=route[5][native_body_variant]
    if (language.index.string_ids[idx] != ORIGINAL_RECOVERY_TITLE_STR_ID
            or language.index.string_ids[idx+native_body_variant+1] != body_id
            or body_id not in ORIGINAL_RECOVERY_BODY_SOURCE_SHA256):
        raise OriginalRecoveryNoticeLanguageError("Original native +18/+1C IDX selector mismatch")
    title=language.strings[ORIGINAL_RECOVERY_TITLE_STR_ID]
    body=language.strings[body_id]
    try:
        title_hash=sha256(title.encode("cp1252")).hexdigest()
        body_hash=sha256(body.encode("cp1252")).hexdigest()
    except UnicodeEncodeError as exc:
        raise OriginalRecoveryNoticeLanguageError("Original source message not native CP1252") from exc
    if (title != ORIGINAL_RECOVERY_TITLE_TEXT
            or title_hash != ORIGINAL_RECOVERY_TITLE_SHA256
            or body_hash != ORIGINAL_RECOVERY_BODY_SOURCE_SHA256[body_id]):
        raise OriginalRecoveryNoticeLanguageError("Original injury return message bytes changed")
    return OriginalRecoveryUnexpandedNoticeTemplates(
        receipt.original_selected_family,receipt.original_event_status,
        native_body_variant,title,body,
    )
