# Recovery536 — original PBg direct-Inbox back_3 source imported, **not yet painted**

## Authorized private original / byte identity
Source: user's original extracted disc folder `FM2001/FM2001_Art/Generic/Background_buttons/back_3.444`, Google Drive private original item ID `1VfoC-TXvAuucq-8NbgnFuqVImIaYe4vR`, under owner-provided source root `1pQy4V8tq5COGhtIMgNPVSDFjSRqiqnTC`. Raw complete file 5,932 bytes, SHA-256 **`f369e73c2a7f9149661d66cf3c781ddc8eabf01f80ef924b423d46d57cf628e6`**, directly revalidated via `sha256sum` on connector-fetched bytes in the working container (no game run). Original EA444 binary header width **40**, height **380**, four 40×95 vertical state images. Git blob SHA `2d0f4b74a6e11dfa2143866ab99544e3bbb71ed6`. No conversion or byte edits.

Native original executable SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`: original `0x5FA570 / 0x5FA5C0` loads original graphic into resource wrapper `0x943B10`; original PBg constructor `0x43092B..0x430957` installs header child ID1 at PBg+0x49C, origin x558 y0; `0x431850` sources width40 height95 via `0x943B24/0x943B28` for native (558,0,40,95) control. ID1 dispatch `0x4326D6` is merged in PR627. Original art path imported byte-identical under `original_assets/source`; original resource provenance recorded in `original_assets/MANIFEST.md`. Hash/EA444 header guard is in `reconstruction/original_pbg_back3_source.py` with tests.

## Native frame status and completeness boundary

Do **not** assume row 0 is always the original neutral/active frame. Button constructor uses raw `0x8018` and its owner/press bitmap state selection depends on additional original-control flags, hover, pressed and disabled transitions that must be traced beyond `0x431850`. No source-correct dynamic visual frame or header caption/indicator is painted yet by the ordinary host. The state mapping cannot be inferred merely by analogy to NEXT `back_5.444` or PMenu `back_4`. Once proven, feed selected original frame into `OriginalGameTkHost`'s management header, with pointer enter/leave/click flags and return behavior tested in real Win11 UI.

This is **EXACT original-byte/source-resource import**, **PARTIAL management Inbox presentation**, **NOT a full rendered header or source-original/Win11 GUI acceptance**. Gates13–17 remain OPEN.
